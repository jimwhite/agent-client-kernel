#!/usr/bin/env python3
"""
Demo script showing the Agent Client Kernel in action.
This simulates what happens when a user interacts with the kernel.
"""

import sys
import os
import time

# Add parent directory to path to import the kernel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_client_kernel import AgentClientKernel


class MockIOPubSocket:
    """Mock IOPub socket for testing."""
    
    def send(self, *args, **kwargs):
        """Print messages instead of sending over ZMQ."""
        pass


class DemoKernel(AgentClientKernel):
    """Modified kernel for demo purposes."""
    
    def __init__(self):
        # Don't call super().__init__ to avoid ZMQ setup
        self.agent_process = None
        self.response_queue = None
        self.reader_thread = None
        self.execution_count = 0
        self.iopub_socket = MockIOPubSocket()
        
    def send_output(self, text):
        """Override to print to stdout."""
        print(f"📤 Output: {text}")
        
    def send_error(self, error_message):
        """Override to print to stderr."""
        print(f"❌ Error: {error_message}", file=sys.stderr)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo():
    """Run the demo."""
    print("\n🚀 Agent Client Kernel Demo")
    print("This demonstrates the kernel interacting with an ACP agent.\n")
    
    kernel = DemoKernel()
    
    # Get path to mock agent
    mock_agent_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tests', 'mock_agent.py'
    )
    
    # Demo 1: Start the agent
    print_section("Demo 1: Starting the Agent")
    print(f"📝 User enters: !start-agent python {mock_agent_path}\n")
    
    result = kernel.do_execute(
        f"!start-agent python {mock_agent_path}",
        silent=False
    )
    
    time.sleep(0.5)  # Give agent time to start
    print(f"\n✅ Status: {result['status']}")
    
    # Demo 2: Send a chat message
    print_section("Demo 2: Sending a Chat Message")
    print("📝 User enters: Hello, can you help me write a function?\n")
    
    result = kernel.do_execute(
        "Hello, can you help me write a function?",
        silent=False
    )
    
    print(f"\n✅ Status: {result['status']}")
    
    # Demo 3: Another message
    print_section("Demo 3: Continuing the Conversation")
    print("📝 User enters: What's the best way to handle errors?\n")
    
    result = kernel.do_execute(
        "What's the best way to handle errors?",
        silent=False
    )
    
    print(f"\n✅ Status: {result['status']}")
    
    # Demo 4: Stop the agent
    print_section("Demo 4: Stopping the Agent")
    print("📝 User enters: !stop-agent\n")
    
    result = kernel.do_execute(
        "!stop-agent",
        silent=False
    )
    
    print(f"\n✅ Status: {result['status']}")
    
    print_section("Demo Complete!")
    print("\n💡 This is how the kernel works in a Jupyter notebook!")
    print("   Each cell execution is a call to do_execute().")
    print("   Agent responses are displayed as notebook output.\n")


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
