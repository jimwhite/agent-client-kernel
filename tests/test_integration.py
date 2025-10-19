#!/usr/bin/env python3
"""
Integration tests for the Agent Client Kernel.
Tests the full workflow of starting an agent, chatting, and stopping.
"""

import os
import sys
import json
import time
import subprocess
import tempfile


def test_kernel_via_console():
    """Test the kernel by running it as a console application."""
    print("Testing kernel via console...")
    
    # This test would require a full Jupyter kernel connection
    # For now, we just verify the module can be run
    result = subprocess.run(
        [sys.executable, '-m', 'agent_client_kernel', '--help'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    # The kernel doesn't have a --help flag, so it will show an error
    # But the fact that it runs without import errors is what we're testing
    print(f"  Exit code: {result.returncode}")
    
    # Check that the module is at least importable and runnable
    assert result.returncode in (0, 2), "Kernel module should be runnable"
    print("✓ Kernel module is runnable")


def test_kernel_spec_installation():
    """Test that the kernel spec is properly installed."""
    print("Testing kernel spec installation...")
    
    result = subprocess.run(
        ['jupyter', 'kernelspec', 'list'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0, "jupyter kernelspec list should succeed"
    assert 'agent_client' in result.stdout, "agent_client kernel should be installed"
    
    print(f"  Kernel spec found in: {result.stdout}")
    print("✓ Kernel spec is properly installed")


def test_full_workflow():
    """Test the complete workflow with the mock agent."""
    print("Testing full workflow...")
    
    # Import the kernel
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent_client_kernel import AgentClientKernel
    
    # Create a mock kernel instance
    class TestKernel(AgentClientKernel):
        def __init__(self):
            self.agent_process = None
            self.response_queue = None
            self.reader_thread = None
            self.execution_count = 0
            self.outputs = []
            self.errors = []
            
        class MockSocket:
            def send(self, *args, **kwargs):
                pass
                
        iopub_socket = MockSocket()
        
        def send_output(self, text):
            self.outputs.append(text)
            
        def send_error(self, error_message):
            self.errors.append(error_message)
    
    kernel = TestKernel()
    
    # Get path to mock agent
    mock_agent_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tests', 'mock_agent.py'
    )
    
    # Test 1: Start agent
    print("  Step 1: Starting agent...")
    result = kernel.do_execute(f"!start-agent python {mock_agent_path}", False)
    assert result['status'] == 'ok', "Starting agent should succeed"
    assert len(kernel.outputs) > 0, "Should have output"
    assert "Agent started" in kernel.outputs[0], "Should confirm agent started"
    print(f"    Output: {kernel.outputs[0]}")
    
    time.sleep(0.5)  # Give agent time to start
    
    # Test 2: Send message
    print("  Step 2: Sending chat message...")
    kernel.outputs.clear()
    result = kernel.do_execute("Hello, test message!", False)
    assert result['status'] == 'ok', "Sending message should succeed"
    
    # Wait for response
    time.sleep(0.5)
    
    assert len(kernel.outputs) > 0, "Should have received response"
    assert "Mock agent received" in kernel.outputs[0], "Should get mock agent response"
    print(f"    Output: {kernel.outputs[0][:80]}...")
    
    # Test 3: Another message
    print("  Step 3: Sending another message...")
    kernel.outputs.clear()
    result = kernel.do_execute("Another test!", False)
    assert result['status'] == 'ok', "Second message should succeed"
    
    time.sleep(0.5)
    assert len(kernel.outputs) > 0, "Should have received second response"
    print(f"    Output: {kernel.outputs[0][:80]}...")
    
    # Test 4: Stop agent
    print("  Step 4: Stopping agent...")
    kernel.outputs.clear()
    result = kernel.do_execute("!stop-agent", False)
    assert result['status'] == 'ok', "Stopping agent should succeed"
    assert len(kernel.outputs) > 0, "Should have output"
    assert "Agent stopped" in kernel.outputs[0], "Should confirm agent stopped"
    print(f"    Output: {kernel.outputs[0]}")
    
    print("✓ Full workflow test passed!")


def test_package_metadata():
    """Test that package metadata is correct."""
    print("Testing package metadata...")
    
    from agent_client_kernel import __version__, AgentClientKernel
    
    assert __version__ == '0.1.0', "Version should match"
    assert AgentClientKernel.implementation == 'AgentClientKernel', "Implementation name should match"
    assert AgentClientKernel.language == 'text', "Language should be text"
    
    print(f"  Version: {__version__}")
    print(f"  Implementation: {AgentClientKernel.implementation}")
    print(f"  Language: {AgentClientKernel.language}")
    print("✓ Package metadata is correct")


if __name__ == "__main__":
    print("\nRunning Integration Tests\n")
    print("=" * 60)
    
    try:
        test_package_metadata()
        print()
        
        test_kernel_via_console()
        print()
        
        test_kernel_spec_installation()
        print()
        
        test_full_workflow()
        print()
        
        print("=" * 60)
        print("All integration tests passed! ✓\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
