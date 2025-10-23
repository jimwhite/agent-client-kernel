"""
The main file for the Agent Client Protocol Jupyter kernel
"""

import asyncio
import asyncio.subprocess as aio_subprocess
import logging
import os
import sys
from pathlib import Path

# Configure logging to output to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

from metakernel import MetaKernel

from acp import (
    Client,
    ClientSideConnection,
    InitializeRequest,
    NewSessionRequest,
    PromptRequest,
    RequestError,
    SessionNotification,
    text_block,
    PROTOCOL_VERSION,
)

# Import nest_asyncio to allow nested event loops
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

from . import __version__, KERNEL_NAME, DISPLAY_NAME


class ACPClient(Client):
    """ACP Client implementation for the Jupyter kernel"""
    
    def __init__(self, kernel) -> None:
        self._kernel = kernel
        self._log = logging.getLogger(__name__)
    
    async def requestPermission(self, params):
        """Handle permission requests from the agent"""
        self._log.info("Permission requested: %s", params)
        
        # Get permission mode from kernel (default: auto)
        mode = getattr(self._kernel, '_permission_mode', 'auto')
        
        # Record the permission request
        if not hasattr(self._kernel, '_permission_history'):
            self._kernel._permission_history = []
        
        if mode == 'deny':
            approved = False
        elif mode == 'manual':
            # TODO: Implement interactive prompting
            # For now, fall back to auto-approve
            approved = True
        else:  # auto mode
            approved = True
        
        self._kernel._permission_history.append({
            'request': str(params),
            'approved': approved
        })
        
        return {"approved": approved}
    
    async def writeTextFile(self, params):
        """Handle file write requests"""
        raise RequestError.method_not_found("fs/write_text_file")
    
    async def readTextFile(self, params):
        """Handle file read requests"""
        raise RequestError.method_not_found("fs/read_text_file")
    
    async def createTerminal(self, params):
        """Handle terminal creation requests"""
        raise RequestError.method_not_found("terminal/create")
    
    async def terminalOutput(self, params):
        """Handle terminal output"""
        raise RequestError.method_not_found("terminal/output")
    
    async def releaseTerminal(self, params):
        """Handle terminal release"""
        raise RequestError.method_not_found("terminal/release")
    
    async def waitForTerminalExit(self, params):
        """Handle terminal exit wait"""
        raise RequestError.method_not_found("terminal/wait_for_exit")
    
    async def killTerminal(self, params):
        """Handle terminal kill"""
        raise RequestError.method_not_found("terminal/kill")
    
    async def sessionUpdate(self, params: SessionNotification) -> None:
        """Handle session updates from the agent"""
        update = params.update
        if isinstance(update, dict):
            kind = update.get("sessionUpdate")
            content = update.get("content")
        else:
            kind = getattr(update, "sessionUpdate", None)
            content = getattr(update, "content", None)
        
        if kind != "agent_message_chunk" or content is None:
            return
        
        if isinstance(content, dict):
            text = content.get("text", "")
        else:
            text = getattr(content, "text", "")
        
        if text:
            # Send output to notebook
            self._kernel._agent_output.append(text)
    
    async def extMethod(self, method: str, params: dict) -> dict:
        """Handle extension method calls"""
        raise RequestError.method_not_found(method)
    
    async def extNotification(self, method: str, params: dict) -> None:
        """Handle extension notifications"""
        pass


class ACPKernel(MetaKernel):
    """Jupyter kernel for Agent Client Protocol"""
    
    implementation = 'Agent Client Protocol'
    implementation_version = __version__
    banner = "Agent Client Protocol Kernel - interact with ACP agents"
    language = 'text'
    language_version = '0.1'
    language_info = {
        'name': 'agent',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
        'help_links': MetaKernel.help_links,
    }
    
    kernel_json = {
        'argv': [sys.executable, '-m', 'agentclientkernel', '-f', '{connection_file}'],
        'display_name': DISPLAY_NAME,
        'language': 'agent',
        'name': KERNEL_NAME
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize the kernel"""
        super(ACPKernel, self).__init__(*args, **kwargs)
        self._log = logging.getLogger(__name__)
        self._log.info("Starting ACP kernel %s", __version__)
        
        # ACP connection tracking
        self._session_id = None
        self._conn = None
        self._proc = None
        self._agent_output = []
        self._event_loop = None
        
        # Agent configuration - can be overridden via environment variables
        self._agent_command = os.environ.get('ACP_AGENT_COMMAND', 'codex-acp')
        self._agent_args = os.environ.get('ACP_AGENT_ARGS', '').split() if os.environ.get('ACP_AGENT_ARGS') else []
        
        # Session configuration
        self._session_cwd = os.getcwd()
        self._mcp_servers = []
        
        # Permission configuration
        self._permission_mode = 'auto'
        self._permission_history = []
        
        # Load custom magics
        self._load_magics()
    
    def _load_magics(self):
        """Load custom magic commands"""
        import importlib
        
        # Load the unified agent magic module
        try:
            module = importlib.import_module('agentclientkernel.magics.agent_magic')
            if hasattr(module, 'register_magics'):
                module.register_magics(self)
                self._log.info("Loaded unified agent magic")
        except Exception as e:
            self._log.error(f"Failed to load agent magic: {e}")
    
    def get_usage(self):
        """Return usage information"""
        return f"""Agent Client Protocol Kernel

This kernel allows interaction with ACP agents directly from Jupyter notebooks.
Simply type your prompts and execute cells to communicate with the agent.

Current agent: {self._agent_command} {' '.join(self._agent_args)}

Agent Management Command:
Use '%agent' with subcommands to manage configuration and sessions:

  MCP Server Configuration:
    %agent mcp add NAME COMMAND [ARGS...]  - add MCP server
    %agent mcp list                        - list MCP servers
    %agent mcp remove NAME                 - remove MCP server
    %agent mcp clear                       - clear all MCP servers

  Permission Configuration:
    %agent permissions [auto|manual|deny]  - set permission mode
    %agent permissions list                - show permission history

  Session Management:
    %agent session new [CWD]               - create new session
    %agent session info                    - show session information
    %agent session restart                 - restart current session

  Agent Configuration:
    %agent config [COMMAND [ARGS...]]     - configure agent command
    %agent env [KEY=VALUE]                 - set environment variables

For detailed help: %agent (shows all subcommands)
For help on any magic: %agent?

Supported agents:
- codex-acp (OpenAI Codex, requires OPENAI_API_KEY or CODEX_API_KEY)
- Any ACP-compatible agent
"""
    
    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        """Get help on an object.  Called by the help magic.
        
        This method provides context-sensitive help for expressions in the kernel.
        It is called by the MetaKernel help system when users type expressions
        followed by '?' or use the %help magic.
        
        Args:
            info: Dictionary containing parsed code information with keys:
                  'code' - the expression to get help on
                  'obj' - the object name
            level: 0 for brief help (docstring), 1 for detailed help
            none_on_fail: If True, return None on failure; otherwise return error message
        
        Returns:
            Help text for the expression, or None/error message if not found
        """
        if not info.get('code'):
            return None if none_on_fail else ''
        
        expr = info.get('obj', info.get('code', '')).strip()
        
        # Check for kernel-specific help topics
        help_topics = {
            'agent': self._get_agent_help(),
            '%agent': self._get_agent_help(),
            'session': self._get_session_help(),
            'mcp': self._get_mcp_help(),
            'permissions': self._get_permissions_help(),
            'config': self._get_config_help(),
        }
        
        # Check if the expression matches a help topic
        for topic, help_text in help_topics.items():
            if expr.lower() == topic.lower() or expr.lower().startswith(topic.lower() + ' '):
                return help_text
        
        # For anything else, provide general kernel help
        if none_on_fail:
            return None
        else:
            return f"""No specific help available for '{expr}'.

Agent Client Protocol Kernel Help
==================================

This kernel provides an interface to Agent Client Protocol (ACP) compatible agents.

Available help topics:
  - agent       : Help on %agent magic command
  - session     : Help on session management
  - mcp         : Help on MCP server configuration
  - permissions : Help on permission management
  - config      : Help on agent configuration

Use '?TOPIC' or '%help TOPIC' to get help on a specific topic.

For general usage: {self.get_usage()}
"""
    
    def _get_agent_help(self):
        """Return help text for the %agent magic command"""
        return f"""Agent Magic Command

The %agent magic provides unified configuration and management for the kernel.

SUBCOMMANDS
===========

MCP Server Configuration:
  %agent mcp add NAME COMMAND [ARGS...]
      Add an MCP (Model Context Protocol) server to the session
      Example: %agent mcp add filesystem /usr/local/bin/mcp-server-filesystem
      
  %agent mcp list
      List all configured MCP servers
      
  %agent mcp remove NAME
      Remove a specific MCP server
      
  %agent mcp clear
      Remove all MCP servers

Permission Configuration:
  %agent permissions [auto|manual|deny]
      Set how permission requests are handled
      - auto: automatically approve all requests (default)
      - manual: prompt for each request (not yet implemented)
      - deny: automatically deny all requests
      
  %agent permissions list
      Show history of permission requests

Session Management:
  %agent session new [CWD]
      Create a new agent session with optional working directory
      Example: %agent session new /path/to/project
      
  %agent session info
      Display information about the current session
      
  %agent session restart
      Restart the current session with same configuration

Agent Configuration:
  %agent config [COMMAND [ARGS...]]
      Configure the agent command to use
      Example: %agent config codex-acp --verbose
      
  %agent env [KEY=VALUE]
      Set environment variables for the agent
      Example: %agent env OPENAI_API_KEY=sk-...

Current Configuration:
  Agent: {self._agent_command} {' '.join(self._agent_args)}
  Session ID: {self._session_id if self._session_id else 'No active session'}
  Working Directory: {self._session_cwd}
"""
    
    def _get_session_help(self):
        """Return help text for session management"""
        return f"""Session Management

Sessions represent an active connection to an ACP agent.

COMMANDS
========
  %agent session new [CWD]
      Create a new session, optionally with a specific working directory
      
  %agent session info
      Display information about the current session
      
  %agent session restart
      Restart the current session

CURRENT SESSION
===============
  Session ID: {self._session_id if self._session_id else 'No active session'}
  Working Directory: {self._session_cwd}
  Agent: {self._agent_command}
"""
    
    def _get_mcp_help(self):
        """Return help text for MCP server configuration"""
        mcp_count = len(self._mcp_servers) if hasattr(self, '_mcp_servers') else 0
        return f"""MCP Server Configuration

MCP (Model Context Protocol) servers provide additional capabilities to the agent.

COMMANDS
========
  %agent mcp add NAME COMMAND [ARGS...]
      Add an MCP server
      
  %agent mcp list
      List configured servers
      
  %agent mcp remove NAME
      Remove a server
      
  %agent mcp clear
      Remove all servers

CURRENT CONFIGURATION
=====================
  Configured MCP servers: {mcp_count}
"""
    
    def _get_permissions_help(self):
        """Return help text for permission management"""
        return f"""Permission Management

Control how the kernel handles permission requests from the agent.

MODES
=====
  auto   - Automatically approve all requests (default)
  manual - Prompt for each request (not yet implemented)
  deny   - Automatically deny all requests

COMMANDS
========
  %agent permissions [MODE]
      Set permission mode
      
  %agent permissions list
      Show permission request history

CURRENT CONFIGURATION
=====================
  Permission Mode: {self._permission_mode}
"""
    
    def _get_config_help(self):
        """Return help text for agent configuration"""
        return f"""Agent Configuration

Configure the ACP agent command and environment.

COMMANDS
========
  %agent config [COMMAND [ARGS...]]
      Set the agent command and arguments
      Example: %agent config codex-acp --verbose
      
  %agent env [KEY=VALUE]
      Set environment variables
      Example: %agent env OPENAI_API_KEY=sk-...

CURRENT CONFIGURATION
=====================
  Agent Command: {self._agent_command}
  Agent Args: {' '.join(self._agent_args) if self._agent_args else '(none)'}

ENVIRONMENT VARIABLES
=====================
  OPENAI_API_KEY: {'✓ set' if os.environ.get('OPENAI_API_KEY') else '✗ not set'}
  CODEX_API_KEY: {'✓ set' if os.environ.get('CODEX_API_KEY') else '✗ not set'}
  ACP_AGENT_COMMAND: {os.environ.get('ACP_AGENT_COMMAND', '(not set)')}
"""
    
    async def _start_agent(self):
        """Start the ACP agent process"""
        if self._proc is not None:
            return
        
        self._log.info("Starting agent: %s %s", self._agent_command, ' '.join(self._agent_args))
        
        # Find the agent executable
        program_path = Path(self._agent_command)
        spawn_program = self._agent_command
        spawn_args = self._agent_args
        
        if program_path.exists() and not os.access(program_path, os.X_OK):
            spawn_program = sys.executable
            spawn_args = [str(program_path), *self._agent_args]
        
        # Start the agent process
        self._proc = await asyncio.create_subprocess_exec(
            spawn_program,
            *spawn_args,
            stdin=aio_subprocess.PIPE,
            stdout=aio_subprocess.PIPE,
            stderr=aio_subprocess.PIPE,
        )
        
        if self._proc.stdin is None or self._proc.stdout is None:
            raise RuntimeError("Agent process does not expose stdio pipes")
        
        # Create client connection
        client_impl = ACPClient(self)
        self._conn = ClientSideConnection(
            lambda _agent: client_impl,
            self._proc.stdin,
            self._proc.stdout
        )
        
        # Initialize the agent
        await self._conn.initialize(
            InitializeRequest(protocolVersion=PROTOCOL_VERSION, clientCapabilities=None)
        )
        
        # Create a new session with MCP servers
        from acp.schema import StdioMcpServer
        
        mcp_servers = []
        for server_config in self._mcp_servers:
            mcp_servers.append(StdioMcpServer(
                name=server_config['name'],
                command=server_config['command'],
                args=server_config['args'],
                env=server_config.get('env', [])
            ))
        
        session = await self._conn.newSession(
            NewSessionRequest(mcpServers=mcp_servers, cwd=self._session_cwd)
        )
        self._session_id = session.sessionId
        
        self._log.info("Agent started with session ID: %s", self._session_id)
    
    async def _stop_agent(self):
        """Stop the ACP agent process"""
        if self._proc is None:
            return
        
        self._log.info("Stopping agent")
        
        if self._proc.returncode is None:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._proc.kill()
                await self._proc.wait()
        
        self._proc = None
        self._conn = None
        self._session_id = None
    
    async def _send_prompt(self, code: str) -> str:
        """Send a prompt to the agent and get the response"""
        # Ensure agent is started
        if self._conn is None or self._session_id is None:
            await self._start_agent()
        
        # Clear previous output
        self._agent_output = []
        
        # Send the prompt
        await self._conn.prompt(
            PromptRequest(
                sessionId=self._session_id,
                prompt=[text_block(code)],
            )
        )
        
        # Wait a bit for the response to accumulate
        await asyncio.sleep(0.5)
        
        # Return the accumulated output
        return ''.join(self._agent_output) if self._agent_output else "No response from agent"
    
    def do_execute_direct(self, code):
        """
        Execute code directly - this is the main entry point for metakernel
        """
        if not code.strip():
            return ""
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async prompt
        try:
            result = loop.run_until_complete(self._send_prompt(code))
            return result
        except Exception as e:
            self._log.error("Error sending prompt: %s", e, exc_info=True)
            return f"Error: {str(e)}\n\nMake sure the ACP agent is configured correctly.\nCurrent agent: {self._agent_command}"
    
    def do_shutdown(self, restart):
        """Shutdown the kernel"""
        # Stop the agent process
        if self._proc is not None:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self._stop_agent())
            except Exception as e:
                self._log.error("Error stopping agent: %s", e)
        
        return super().do_shutdown(restart)
    
    def repr(self, data):
        """Return string representation of data"""
        return str(data)

