# Agent Client Kernel Usage Example

This example demonstrates how to use the Agent Client Kernel to interact with an ACP-compliant agent from a Jupyter notebook.

## Setup

1. Install the kernel:
```bash
pip install -e .
python -m agent_client_kernel.install --user
```

2. Start Jupyter:
```bash
jupyter notebook
# or
jupyter lab
```

3. Create a new notebook and select "Agent Client Protocol" as the kernel.

## Example Session

### Cell 1: Start the Agent

To start an agent, use the `!start-agent` command followed by the path to your agent executable:

```
!start-agent python /path/to/your/agent.py
```

For testing purposes, you can use the included mock agent:

```
!start-agent python tests/mock_agent.py
```

**Output:**
```
Agent started successfully.
```

### Cell 2: Send a Chat Message

Once the agent is started, you can send chat messages by simply typing in the cell:

```
Hello, can you help me write a Python function?
```

**Output:**
```
Mock agent received: 'Hello, can you help me write a Python function?'
This is a test response from the mock agent.
```

### Cell 3: Continue the Conversation

```
What's the best way to read a CSV file?
```

**Output:**
```
Mock agent received: 'What's the best way to read a CSV file?'
This is a test response from the mock agent.
```

### Cell 4: Stop the Agent

When you're done, stop the agent:

```
!stop-agent
```

**Output:**
```
Agent stopped.
```

## Special Commands

- `!start-agent <command> [args...]` - Start an ACP agent process
- `!stop-agent` - Stop the currently running agent

## Using with Real ACP Agents

To use with a real ACP-compliant agent:

1. Install or build your ACP agent
2. Start it with the `!start-agent` command:
   ```
   !start-agent /path/to/agent --option1 value1 --option2 value2
   ```
3. Start chatting with the agent

The kernel will:
- Send your messages as JSON-RPC requests to the agent
- Display agent responses in the notebook output
- Support agent dialogs and file system interactions
- Maintain the conversation context throughout the session

## Troubleshooting

### Agent not starting
- Check that the agent path is correct
- Verify the agent has execute permissions
- Look for error messages in the notebook output

### No response from agent
- Ensure the agent is running (`!start-agent` should have succeeded)
- Check that the agent is implementing the ACP protocol correctly
- The kernel waits up to 30 seconds for a response

### Agent crashes
- Check the agent's stderr output (may appear in the notebook or terminal)
- Restart the agent with `!start-agent`
