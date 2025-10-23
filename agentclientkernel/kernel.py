"""
The main file for the Agent Client Protocol Jupyter kernel
"""

import asyncio
import logging
from uuid import uuid4

from ipykernel.kernelbase import Kernel

from acp import (
    Agent,
    AgentSideConnection,
    InitializeRequest,
    InitializeResponse,
    NewSessionRequest,
    NewSessionResponse,
    PromptRequest,
    PromptResponse,
    session_notification,
    text_block,
    update_agent_message,
)

from . import __version__


class SimpleAgent(Agent):
    """A simple echo agent for demonstration"""
    
    def __init__(self, conn):
        self._conn = conn
        self._session_id = None
    
    async def initialize(self, params: InitializeRequest) -> InitializeResponse:
        return InitializeResponse(protocolVersion=params.protocolVersion)
    
    async def newSession(self, params: NewSessionRequest) -> NewSessionResponse:
        self._session_id = uuid4().hex
        return NewSessionResponse(sessionId=self._session_id)
    
    async def prompt(self, params: PromptRequest) -> PromptResponse:
        """Echo back the prompt"""
        for block in params.prompt:
            text = getattr(block, "text", "")
            await self._conn.sessionUpdate(
                session_notification(
                    params.sessionId,
                    update_agent_message(text_block(f"Echo: {text}")),
                )
            )
        return PromptResponse(stopReason="end_turn")


class ACPKernel(Kernel):
    """Jupyter kernel for Agent Client Protocol"""
    
    implementation = 'Agent Client Protocol'
    implementation_version = __version__
    banner = "Agent Client Protocol Kernel - interact with ACP agents"
    language = 'text'
    language_version = '0.1'
    language_info = {
        'name': 'agent',
        'mimetype': 'text/plain'
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize the kernel"""
        super(ACPKernel, self).__init__(*args, **kwargs)
        self._log = logging.getLogger(__name__)
        self._log.info("Starting ACP kernel %s", __version__)
        
        # Session tracking
        self._session_id = None
        self._responses = []
    
    def _send_output(self, text, stream='stdout'):
        """Send output to the frontend"""
        stream_content = {'name': stream, 'text': text}
        self.send_response(self.iopub_socket, 'stream', stream_content)
    
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        """
        Execute user code
        """
        if not code.strip():
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
        
        if not silent:
            # Send the input as echo
            self._send_output(f"Input: {code}\n")
            
            # Simple echo response for now
            self._send_output(f"Echo: {code}\n")
        
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }
    
    def do_complete(self, code, cursor_pos):
        """Handle code completion requests"""
        return {
            'status': 'ok',
            'matches': [],
            'cursor_start': cursor_pos,
            'cursor_end': cursor_pos,
            'metadata': {}
        }
    
    def do_inspect(self, code, cursor_pos, detail_level=0):
        """Handle inspection requests"""
        return {
            'status': 'ok',
            'data': {},
            'metadata': {},
            'found': False
        }
