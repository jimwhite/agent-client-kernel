# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-19

### Added
- Initial release of Agent Client Kernel
- Jupyter kernel implementation for Agent Client Protocol (ACP)
- JSON-RPC communication over stdin/stdout with agents
- Support for starting and stopping agent processes from notebook cells
- Chat interface for interacting with agents
- Special commands: `!start-agent` and `!stop-agent`
- Mock agent for testing and development
- Basic test suite
- Documentation and examples
- Setup script and kernel installation tool

### Features
- Execute user messages as chat input to the agent
- Display agent responses in notebook output
- Thread-safe message queuing for agent responses
- Error handling and user feedback
- Support for any ACP-compliant agent

### Documentation
- README with installation and usage instructions
- ARCHITECTURE document explaining the design
- CONTRIBUTING guide for developers
- Example usage documentation
- Inline code documentation

[0.1.0]: https://github.com/jimwhite/agent-client-kernel/releases/tag/v0.1.0
