#!/usr/bin/env python3
"""
Simple test for the Agent Client Kernel.
"""

import os
import sys
import json
import subprocess
import tempfile


def test_mock_agent():
    """Test that the mock agent works correctly."""
    print("Testing mock agent...")
    
    # Start the mock agent
    agent_path = os.path.join(os.path.dirname(__file__), 'mock_agent.py')
    agent = subprocess.Popen(
        [sys.executable, agent_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send a test request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "chat/send",
        "params": {
            "message": "Hello, agent!"
        }
    }
    
    agent.stdin.write(json.dumps(request) + '\n')
    agent.stdin.flush()
    
    # Read the response
    response_line = agent.stdout.readline()
    response = json.loads(response_line)
    
    print(f"Request: {request}")
    print(f"Response: {response}")
    
    # Check the response
    assert response['jsonrpc'] == '2.0'
    assert response['id'] == 1
    assert 'result' in response
    assert 'text' in response['result']
    assert 'Mock agent received' in response['result']['text']
    
    # Cleanup
    agent.terminate()
    agent.wait()
    
    print("✓ Mock agent test passed!")


def test_kernel_import():
    """Test that the kernel can be imported."""
    print("Testing kernel import...")
    
    try:
        from agent_client_kernel import AgentClientKernel
        print(f"✓ Successfully imported AgentClientKernel: {AgentClientKernel}")
    except Exception as e:
        print(f"✗ Failed to import AgentClientKernel: {e}")
        sys.exit(1)


def test_kernel_instance():
    """Test that we can create a kernel instance."""
    print("Testing kernel instantiation...")
    
    try:
        from agent_client_kernel import AgentClientKernel
        kernel = AgentClientKernel()
        print(f"✓ Successfully created kernel instance")
        print(f"  Implementation: {kernel.implementation}")
        print(f"  Version: {kernel.implementation_version}")
        print(f"  Language: {kernel.language}")
    except Exception as e:
        print(f"✗ Failed to create kernel instance: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Running Agent Client Kernel Tests\n")
    print("=" * 60)
    
    test_kernel_import()
    print()
    
    test_kernel_instance()
    print()
    
    test_mock_agent()
    print()
    
    print("=" * 60)
    print("All tests passed! ✓")
