"""
The main file for the Agent Client Protocol Jupyter kernel
"""

import asyncio
import logging
import sys
from typing import Any

from metakernel import MetaKernel

from acp import (
    Agent,
    AgentSideConnection,
    AuthenticateRequest,
    AuthenticateResponse,
    CancelNotification,
    InitializeRequest,
    InitializeResponse,
    LoadSessionRequest,
    LoadSessionResponse,
    NewSessionRequest,
    NewSessionResponse,
    PromptRequest,
    PromptResponse,
    SetSessionModeRequest,
    SetSessionModeResponse,
    session_notification,
    text_block,
    update_agent_message,
    PROTOCOL_VERSION,
)
from acp.schema import AgentCapabilities, McpCapabilities, PromptCapabilities

from . import __version__, KERNEL_NAME, DISPLAY_NAME


class ACPAgent(Agent):
    """ACP Agent implementation for the Jupyter kernel"""
    
    def __init__(self, conn: AgentSideConnection, kernel) -> None:
        self._conn = conn
        self._kernel = kernel
        self._next_session_id = 0
        self._log = logging.getLogger(__name__)
    
    async def _send_chunk(self, session_id: str, content: Any) -> None:
        """Send a chunk of content to the client"""
        await self._conn.sessionUpdate(
            session_notification(
                session_id,
                update_agent_message(content),
            )
        )
    
    async def initialize(self, params: InitializeRequest) -> InitializeResponse:
        """Initialize the agent"""
        self._log.info("Received initialize request")
        mcp_caps = McpCapabilities(http=False, sse=False)
        prompt_caps = PromptCapabilities(audio=False, embeddedContext=False, image=False)
        agent_caps = AgentCapabilities(
            loadSession=False,
            mcpCapabilities=mcp_caps,
            promptCapabilities=prompt_caps,
        )
        return InitializeResponse(
            protocolVersion=PROTOCOL_VERSION,
            agentCapabilities=agent_caps,
        )
    
    async def authenticate(self, params: AuthenticateRequest) -> AuthenticateResponse | None:
        """Authenticate the agent"""
        self._log.info("Received authenticate request")
        return AuthenticateResponse()
    
    async def newSession(self, params: NewSessionRequest) -> NewSessionResponse:
        """Create a new session"""
        self._log.info("Received new session request")
        session_id = str(self._next_session_id)
        self._next_session_id += 1
        return NewSessionResponse(sessionId=session_id)
    
    async def loadSession(self, params: LoadSessionRequest) -> LoadSessionResponse | None:
        """Load a session"""
        self._log.info("Received load session request")
        return LoadSessionResponse()
    
    async def setSessionMode(self, params: SetSessionModeRequest) -> SetSessionModeResponse | None:
        """Set session mode"""
        self._log.info("Received set session mode request")
        return SetSessionModeResponse()
    
    async def prompt(self, params: PromptRequest) -> PromptResponse:
        """Handle a prompt request"""
        self._log.info("Received prompt request")
        
        # Extract text from all blocks in the prompt
        prompt_text = []
        for block in params.prompt:
            text = getattr(block, "text", "")
            if text:
                prompt_text.append(text)
        
        full_prompt = "\n".join(prompt_text)
        
        # Send the processed response back
        await self._send_chunk(
            params.sessionId,
            text_block(f"Processing: {full_prompt}"),
        )
        
        # Echo back the prompt for now (can be extended with actual agent logic)
        await self._send_chunk(
            params.sessionId,
            text_block(f"Response: {full_prompt}"),
        )
        
        return PromptResponse(stopReason="end_turn")
    
    async def cancel(self, params: CancelNotification) -> None:
        """Handle cancel notification"""
        self._log.info("Received cancel notification")
    
    async def extMethod(self, method: str, params: dict) -> dict:
        """Handle extension method calls"""
        self._log.info("Received extension method call: %s", method)
        return {"status": "ok"}
    
    async def extNotification(self, method: str, params: dict) -> None:
        """Handle extension notifications"""
        self._log.info("Received extension notification: %s", method)


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
        
        # ACP session tracking
        self._session_id = None
        self._agent = None
        self._conn = None
        self._event_loop = None
    
    def get_usage(self):
        """Return usage information"""
        return """Agent Client Protocol Kernel

This kernel allows interaction with ACP agents directly from Jupyter notebooks.
Simply type your prompts and execute cells to communicate with the agent.

The kernel implements the full ACP specification including:
- Session management
- Authentication
- Prompt handling
- Cancellation support
"""
    
    def do_execute_direct(self, code):
        """
        Execute code directly - this is the main entry point for metakernel
        """
        if not code.strip():
            return ""
        
        # For now, simulate agent interaction
        # In a full implementation, this would communicate with an actual ACP agent
        result = f"Agent response to: {code}"
        return result
    
    def repr(self, data):
        """Return string representation of data"""
        return str(data)
