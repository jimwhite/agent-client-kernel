# Contributing to Agent Client Kernel

Thank you for your interest in contributing to the Agent Client Kernel! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jimwhite/agent-client-kernel.git
   cd agent-client-kernel
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

4. **Install the kernel spec**:
   ```bash
   python -m agent_client_kernel.install --user
   ```

5. **Verify installation**:
   ```bash
   jupyter kernelspec list
   ```

## Running Tests

Run the test suite:

```bash
python tests/test_kernel.py
```

Test with a Jupyter notebook:

```bash
jupyter notebook
# Create a new notebook with "Agent Client Protocol" kernel
# Test with the mock agent: !start-agent python tests/mock_agent.py
```

## Making Changes

### Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for agent initialization handshake

- Implement initialize method in kernel
- Add handshake to agent startup sequence
- Update documentation
```

### Testing

- Add tests for new features
- Ensure existing tests still pass
- Test manually with both mock and real agents
- Test edge cases and error conditions

## Areas for Contribution

### High Priority

1. **Enhanced Protocol Support**
   - Implement full ACP initialization handshake
   - Add support for agent capabilities negotiation
   - Handle agent notifications and events

2. **User Experience**
   - Add progress indicators for long operations
   - Improve error messages
   - Add syntax highlighting for agent responses
   - Support for markdown rendering in responses

3. **Testing**
   - Add unit tests for all kernel methods
   - Create integration tests with real agents
   - Add CI/CD pipeline

### Medium Priority

4. **Rich Output**
   - Support for images and diagrams
   - HTML/JavaScript output
   - Interactive widgets

5. **File System Integration**
   - Display file operation notifications
   - Approve/deny file operations
   - Show diffs for file changes

6. **Multi-Agent Support**
   - Manage multiple concurrent agents
   - Switch between agents
   - Merge responses from multiple agents

### Low Priority

7. **Session Persistence**
   - Save/restore agent state
   - Conversation history
   - Session export/import

8. **Agent Discovery**
   - Auto-discover ACP agents on the system
   - Agent configuration UI
   - Agent marketplace integration

## Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** with clear commits
3. **Update documentation** if needed
4. **Run tests** to ensure nothing breaks
5. **Submit a pull request** with:
   - Clear description of changes
   - Motivation/use case
   - Testing performed
   - Screenshots (if UI changes)

## Code Review

All contributions go through code review. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation
- Backward compatibility
- Security implications

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.
