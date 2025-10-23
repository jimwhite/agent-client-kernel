# agent-client-kernel

A Jupyter Kernel for the Agent Client Protocol (ACP)

This kernel allows you to interact with ACP agents directly from Jupyter notebooks.

## Installation

```bash
pip install -e .
python -m agentclientkernel.install --user
```

Or use the entry point:

```bash
jupyter-agentclientkernel install --user
```

## Usage

After installation, you can create a new notebook and select "Agent Client Protocol" as the kernel.

Type your prompts in cells and execute them to interact with the agent.

## Development

This project provides a minimal working integration between Jupyter and the Agent Client Protocol.

### Requirements

- Python >= 3.10
- ipykernel >= 4.0
- jupyter-client >= 4.0  
- agent-client-protocol >= 0.4.0

## Uninstallation

```bash
jupyter-agentclientkernel remove
```

## License

MIT
