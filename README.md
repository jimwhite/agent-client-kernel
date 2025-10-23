# agent-client-kernel

A Jupyter Kernel for the Agent Client Protocol (ACP)

This kernel allows you to interact with ACP agents directly from Jupyter notebooks. It provides a working integration between Jupyter and the [Agent Client Protocol](https://github.com/PsiACE/agent-client-protocol-python) using [MetaKernel](https://github.com/Calysto/metakernel) as the base.

## About

This project implements a Jupyter kernel that serves coding agents via the Agent Client Protocol. The implementation uses MetaKernel as the base class, which provides built-in magics, shell commands, and other useful features.

## Features

- Full ACP agent implementation with proper session management
- Based on MetaKernel for enhanced functionality
- Support for initialize, authenticate, newSession, and prompt operations
- Compatible with JupyterLab and Jupyter Notebook
- Built-in MetaKernel magics (help, shell, file operations, etc.)

## Installation

Install the package and kernel:

```bash
pip install -e .
python -m agentclientkernel install --user
```

## Usage

After installation, you can create a new notebook and select "Agent Client Protocol" as the kernel.

Type your prompts in cells and execute them to interact with the agent.

See the example notebook in `examples/basic_usage.ipynb` for a demonstration.

## Development

This project provides a working integration between Jupyter and the Agent Client Protocol using MetaKernel.

### Project Structure

```
agentclientkernel/
├── __init__.py        # Package metadata
├── __main__.py        # Entry point for kernel application
├── kernel.py          # Main kernel and agent implementation
└── resources/         # Kernel logos and resources
```

### Requirements

- Python >= 3.10
- ipykernel >= 4.0
- jupyter-client >= 4.0  
- agent-client-protocol >= 0.4.0
- metakernel >= 0.30.0

## Uninstallation

```bash
jupyter kernelspec remove agentclient
pip uninstall agentclientkernel
```

## License

MIT
