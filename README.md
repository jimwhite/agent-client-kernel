# agent-client-kernel

A Jupyter Kernel for the Agent Client Protocol (ACP)

This kernel allows you to interact with ACP agents directly from Jupyter notebooks. It provides a minimal working integration between Jupyter and the [Agent Client Protocol](https://github.com/PsiACE/agent-client-protocol-python).

## About

This project implements a Jupyter kernel that serves coding agents via the Agent Client Protocol. The implementation is based on the structure of the [AIML Chatbot Kernel](https://github.com/paulovn/aiml-chatbot-kernel) example, providing a clean and minimal integration.

## Features

- Simple Jupyter kernel interface for ACP agents
- Easy installation using pip
- Echo-based demonstration agent (extensible for real agents)
- Compatible with JupyterLab and Jupyter Notebook

## Installation

Install the package and kernel:

```bash
pip install -e .
python -m agentclientkernel install --user
```

Or use the entry point:

```bash
jupyter-agentclientkernel install --user
```

## Usage

After installation, you can create a new notebook and select "Agent Client Protocol" as the kernel.

Type your prompts in cells and execute them to interact with the agent.

See the example notebook in `examples/basic_usage.ipynb` for a demonstration.

## Development

This project provides a minimal working integration between Jupyter and the Agent Client Protocol.

### Project Structure

```
agentclientkernel/
├── __init__.py        # Package metadata
├── __main__.py        # Entry point for kernel application
├── kernel.py          # Main kernel implementation
├── install.py         # Installation utilities
└── resources/         # Kernel logos and resources
```

### Requirements

- Python >= 3.10
- ipykernel >= 4.0
- jupyter-client >= 4.0  
- agent-client-protocol >= 0.4.0

## Uninstallation

```bash
jupyter-agentclientkernel remove
pip uninstall agentclientkernel
```

## License

MIT
