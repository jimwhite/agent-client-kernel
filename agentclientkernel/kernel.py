"""
The main file for the Agent Client Protocol Jupyter kernel
"""

import asyncio
import asyncio.subprocess as aio_subprocess
import logging
import os
import sys
from pathlib import Path

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
        # For now, auto-approve all permissions
        # In a real implementation, this should prompt the user
        return {"approved": True}
    
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
    
    def get_usage(self):
        """Return usage information"""
        return f"""Agent Client Protocol Kernel

This kernel allows interaction with ACP agents directly from Jupyter notebooks.
Simply type your prompts and execute cells to communicate with the agent.

Current agent: {self._agent_command} {' '.join(self._agent_args)}

Configuration:
- Set ACP_AGENT_COMMAND environment variable to change the agent command
- Set ACP_AGENT_ARGS environment variable to pass additional arguments
- Example: ACP_AGENT_COMMAND=codex-acp ACP_AGENT_ARGS="--verbose"

Supported agents:
- codex-acp (OpenAI Codex, requires OPENAI_API_KEY or CODEX_API_KEY)
- Any ACP-compatible agent
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
        
        # Create a new session
        session = await self._conn.newSession(
            NewSessionRequest(mcpServers=[], cwd=os.getcwd())
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

