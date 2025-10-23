# agent-client-kernel

A Jupyter Kernel for the Agent Client Protocol (ACP)

This kernel allows you to interact with external ACP agents directly from Jupyter notebooks. It acts as an ACP client that connects to coding agents like [Codex](https://github.com/zed-industries/codex-acp), providing a seamless notebook interface for AI-powered coding assistance.

## About

This project implements a Jupyter kernel that serves as a client for coding agents via the Agent Client Protocol. The implementation uses [MetaKernel](https://github.com/Calysto/metakernel) as the base class, which provides built-in magics, shell commands, and other useful features.

The kernel spawns and communicates with external ACP agents (such as codex-acp) via stdio, allowing you to interact with AI coding assistants directly from your notebook.

## Features

- **ACP Client Implementation**: Full client-side ACP protocol support
- **External Agent Integration**: Connects to any ACP-compatible agent
- **Codex Support**: Works with OpenAI Codex out of the box
- **Based on MetaKernel**: Built-in magics (help, shell, file operations, etc.)
- **Configurable**: Easily switch between different agents via environment variables
- **Compatible with JupyterLab and Jupyter Notebook**

## Installation

Install the package:

```bash
pip install -e .
```

Install the kernel:

```bash
python -m agentclientkernel install --user
```

## Configuration

The kernel connects to external ACP agents. By default, it uses `codex-acp`.

### Using Codex (Default)

1. Install codex-acp:
   ```bash
   npm install -g @zed-industries/codex-acp
   # or download from https://github.com/zed-industries/codex-acp/releases
   ```

2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

3. Start Jupyter and use the "Agent Client Protocol" kernel

### Using Other Agents

Set environment variables to configure a different agent:

```bash
export ACP_AGENT_COMMAND=path/to/your/agent
export ACP_AGENT_ARGS="--arg1 --arg2"
```

Then start Jupyter normally. The kernel will use your configured agent.

## Usage

After installation, create a new notebook and select "Agent Client Protocol" as the kernel.

Type your prompts in cells and execute them to interact with the agent:

```
Create a Python function to calculate fibonacci numbers
```

The agent will respond with code, explanations, and can help with:
- Writing code
- Debugging
- Code review
- Refactoring
- Documentation
- And more!

See the example notebook in `examples/basic_usage.ipynb` for a demonstration.

## Requirements

- Python >= 3.10
- ipykernel >= 4.0
- jupyter-client >= 4.0  
- agent-client-protocol >= 0.4.0
- metakernel >= 0.30.0
- An ACP-compatible agent (e.g., codex-acp)

## Uninstallation

```bash
jupyter kernelspec remove agentclient
pip uninstall agentclientkernel
```

## License

MIT
