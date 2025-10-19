# Agent Client Kernel

A Jupyter kernel implementation that acts as a client for the Zed Agent Client Protocol (ACP). This kernel allows users to interact with AI coding agents directly from Jupyter notebooks by entering chat messages in notebook cells.

## Features

- **Chat Interface**: Interact with ACP agents through notebook cells
- **JSON-RPC Communication**: Full support for the Agent Client Protocol over stdin/stdout
- **Agent Output Display**: View agent responses, dialogs, and file system interactions in notebook output
- **Session Management**: Start and stop agent processes from within the notebook

## Installation

1. Install the package:
```bash
pip install -e .
```

2. Install the kernel spec:
```bash
python -m agent_client_kernel.install --user
```

Or use the provided script:
```bash
agent-client-kernel --user
```

## Usage

1. Start Jupyter Notebook or JupyterLab:
```bash
jupyter notebook
# or
jupyter lab
```

2. Create a new notebook and select "Agent Client Protocol" as the kernel

3. Start an agent process:
```
!start-agent /path/to/agent-executable
```

4. Chat with the agent by entering messages in cells:
```
Can you help me write a Python function?
```

5. Stop the agent when done:
```
!stop-agent
```

## Agent Client Protocol

This kernel implements a client for the [Agent Client Protocol](https://agentclientprotocol.com/), which provides a standardized way for code editors and tools to communicate with AI coding agents via JSON-RPC.

The protocol enables:
- Real-time communication with agents
- File system operations
- Interactive dialogs
- Tool and resource access

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/jimwhite/agent-client-kernel.git
cd agent-client-kernel

# Install in development mode
pip install -e .

# Install the kernel spec
python -m agent_client_kernel.install --user
```

## Requirements

- Python 3.8+
- ipykernel >= 6.0.0
- jupyter-client >= 7.0.0

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
