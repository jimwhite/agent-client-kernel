# Architecture

This document describes the architecture of the Agent Client Kernel.

## Overview

The Agent Client Kernel is a Jupyter kernel that implements a client for the Agent Client Protocol (ACP). It allows users to interact with AI coding agents directly from Jupyter notebooks, using notebook cells as a chat interface.

## Components

### 1. Kernel (`agent_client_kernel/kernel.py`)

The `AgentClientKernel` class extends `ipykernel.kernelbase.Kernel` and provides:

- **Kernel Interface**: Implements the Jupyter kernel protocol for executing code
- **Process Management**: Starts and manages ACP agent processes
- **JSON-RPC Communication**: Sends and receives JSON-RPC messages via stdin/stdout
- **Response Handling**: Queues and processes agent responses
- **Output Display**: Sends agent output to the notebook

Key methods:
- `start_agent(agent_command)`: Launches the agent process
- `send_to_agent(message)`: Sends JSON-RPC messages to the agent
- `do_execute(code, ...)`: Main execution method called by Jupyter
- `_read_agent_output()`: Background thread for reading agent responses

### 2. Installation (`agent_client_kernel/install.py`)

Provides functionality to install the kernel specification into Jupyter:

- Uses `jupyter_client.kernelspec.KernelSpecManager`
- Supports user-level and system-level installation
- Command-line interface for easy installation

### 3. Kernel Specification (`agent_client_kernel/kernelspec/kernel.json`)

Defines the kernel metadata for Jupyter:

```json
{
  "argv": ["python", "-m", "agent_client_kernel", "-f", "{connection_file}"],
  "display_name": "Agent Client Protocol",
  "language": "agent-chat"
}
```

## Communication Flow

### Starting an Agent

```
User Cell: !start-agent python agent.py
    ↓
Kernel.do_execute()
    ↓
Kernel.start_agent()
    ↓
subprocess.Popen() → Agent Process
    ↓
Start reader thread (_read_agent_output)
    ↓
Output: "Agent started successfully."
```

### Sending a Chat Message

```
User Cell: "Hello, agent!"
    ↓
Kernel.do_execute()
    ↓
Create JSON-RPC request:
{
  "jsonrpc": "2.0",
  "id": N,
  "method": "chat/send",
  "params": {"message": "Hello, agent!"}
}
    ↓
Kernel.send_to_agent()
    ↓
Write to agent.stdin
    ↓
Reader thread reads from agent.stdout
    ↓
Response queued in response_queue
    ↓
Parse JSON-RPC response
    ↓
Display in notebook output
```

## JSON-RPC Protocol

The kernel communicates with agents using JSON-RPC 2.0 over stdin/stdout:

### Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "chat/send",
  "params": {
    "message": "User's chat message"
  }
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "text": "Agent's response text"
  }
}
```

### Error Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## Threading Model

The kernel uses a multi-threaded approach:

1. **Main Thread**: Handles Jupyter kernel protocol and executes user code
2. **Reader Thread**: Continuously reads output from the agent's stdout
3. **Queue**: Thread-safe queue for passing responses between threads

```
┌─────────────────────┐
│  Jupyter Notebook   │
└──────────┬──────────┘
           │ Kernel Protocol
           ↓
┌─────────────────────┐
│   Main Thread       │
│  (Kernel.do_execute)│
├─────────────────────┤
│  • Parse user input │
│  • Send to agent    │
│  • Format output    │
└──────────┬──────────┘
           │
           ↓
    ┌─────────────┐
    │   Queue     │
    └─────┬───────┘
          ↑
          │
┌─────────┴─────────┐
│  Reader Thread    │
│(_read_agent_output)│
├───────────────────┤
│  • Read stdout    │
│  • Queue responses│
└─────────┬─────────┘
          │
          ↓
    ┌─────────────┐
    │Agent Process│
    │  (stdin/out)│
    └─────────────┘
```

## Special Commands

The kernel recognizes special commands prefixed with `!`:

- `!start-agent <command> [args...]`: Start an agent process
- `!stop-agent`: Terminate the current agent process

These commands are intercepted in `do_execute()` before being sent to the agent.

## Extension Points

The kernel can be extended to support:

1. **Additional ACP Methods**: Add new method handlers in `send_to_agent()`
2. **Rich Output**: Support for images, HTML, and other MIME types
3. **Tool Integration**: Handle tool requests from agents
4. **File System Operations**: Support for file read/write notifications
5. **Multiple Agents**: Manage multiple concurrent agent connections

## Security Considerations

1. **Process Isolation**: Agents run as separate processes
2. **User-Initiated**: Agents must be explicitly started by users
3. **Input Validation**: JSON-RPC messages are validated before sending
4. **Error Handling**: Exceptions are caught and displayed as errors
5. **Resource Limits**: Subprocess timeouts prevent hanging

## Future Enhancements

Potential improvements:

- [ ] Support for agent initialization handshake
- [ ] Better error messages and diagnostics
- [ ] Progress indicators for long-running operations
- [ ] Interrupt handling for canceling operations
- [ ] Session persistence across notebook restarts
- [ ] Multi-agent support (chat with multiple agents)
- [ ] Rich media support (images, diagrams, etc.)
- [ ] Tool approval UI for file system operations
- [ ] Agent discovery and auto-configuration
