"""Jupyter kernel for Agent Client Protocol."""

import json
import subprocess
import threading
import queue
from ipykernel.kernelbase import Kernel


class AgentClientKernel(Kernel):
    """A Jupyter kernel that acts as an ACP client."""
    
    implementation = 'AgentClientKernel'
    implementation_version = '0.1.0'
    language = 'text'
    language_version = '1.0'
    language_info = {
        'name': 'agent-chat',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
    }
    banner = "Agent Client Protocol Kernel - Chat with your AI coding agent"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent_process = None
        self.response_queue = queue.Queue()
        self.reader_thread = None
        self.execution_count = 0
        
    def start_agent(self, agent_command):
        """Start the ACP agent server process."""
        if self.agent_process is not None:
            return
            
        try:
            # Initialize the response queue if not already done
            if self.response_queue is None:
                self.response_queue = queue.Queue()
                
            self.agent_process = subprocess.Popen(
                agent_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start a thread to read responses from the agent
            self.reader_thread = threading.Thread(target=self._read_agent_output, daemon=True)
            self.reader_thread.start()
            
        except Exception as e:
            self.send_error(f"Failed to start agent: {str(e)}")
            
    def _read_agent_output(self):
        """Read output from the agent process."""
        while self.agent_process and self.agent_process.poll() is None:
            try:
                line = self.agent_process.stdout.readline()
                if line:
                    self.response_queue.put(line.strip())
            except Exception as e:
                self.response_queue.put(f"Error reading agent output: {str(e)}")
                break
                
    def send_to_agent(self, message):
        """Send a JSON-RPC message to the agent."""
        if self.agent_process is None:
            return None
            
        try:
            json_message = json.dumps(message) + '\n'
            self.agent_process.stdin.write(json_message)
            self.agent_process.stdin.flush()
            
            # Wait for response (with timeout)
            import time
            timeout = 30
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response_line = self.response_queue.get(timeout=0.1)
                    try:
                        return json.loads(response_line)
                    except json.JSONDecodeError:
                        # If not valid JSON, it might be a notification or partial response
                        # Continue reading
                        pass
                except queue.Empty:
                    continue
                    
            return None
            
        except Exception as e:
            self.send_error(f"Failed to communicate with agent: {str(e)}")
            return None
            
    def send_error(self, error_message):
        """Send an error message to the notebook."""
        self.send_response(
            self.iopub_socket,
            'stream',
            {
                'name': 'stderr',
                'text': error_message + '\n'
            }
        )
        
    def send_output(self, text):
        """Send output text to the notebook."""
        self.send_response(
            self.iopub_socket,
            'stream',
            {
                'name': 'stdout',
                'text': text + '\n'
            }
        )
        
    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        """Execute code (chat message) in the kernel."""
        if not code.strip():
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
            
        # Check for special commands
        if code.strip().startswith('!start-agent'):
            parts = code.strip().split(None, 1)
            if len(parts) > 1:
                agent_command = parts[1].split()
                self.start_agent(agent_command)
                self.send_output("Agent started successfully.")
            else:
                self.send_error("Usage: !start-agent <command> [args...]")
            
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
            
        if code.strip() == '!stop-agent':
            if self.agent_process:
                self.agent_process.terminate()
                self.agent_process = None
                self.send_output("Agent stopped.")
            else:
                self.send_output("No agent is running.")
                
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
            
        # If no agent is running, show help
        if self.agent_process is None:
            self.send_output("No agent is running. Start an agent with:")
            self.send_output("!start-agent <path-to-agent-executable>")
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
            
        # Send the code as a chat message to the agent
        # This is a simplified version - actual ACP protocol would need proper JSON-RPC formatting
        message = {
            "jsonrpc": "2.0",
            "id": self.execution_count,
            "method": "chat/send",
            "params": {
                "message": code
            }
        }
        
        response = self.send_to_agent(message)
        
        if response:
            # Display the agent's response
            if 'result' in response:
                result = response['result']
                if isinstance(result, dict) and 'text' in result:
                    self.send_output(result['text'])
                else:
                    self.send_output(json.dumps(result, indent=2))
            elif 'error' in response:
                error = response['error']
                self.send_error(f"Agent error: {error.get('message', str(error))}")
            else:
                self.send_output(json.dumps(response, indent=2))
        else:
            self.send_error("No response from agent")
            
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }
        
    def do_shutdown(self, restart):
        """Shutdown the kernel and agent."""
        if self.agent_process:
            self.agent_process.terminate()
            self.agent_process = None
        return {'status': 'ok', 'restart': restart}
