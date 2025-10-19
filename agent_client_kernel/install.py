"""Installation script for the kernel spec."""

import argparse
import json
import os
import sys
import shutil
from jupyter_client.kernelspec import KernelSpecManager


def install_kernel_spec(user=True, prefix=None):
    """Install the kernel spec."""
    # Get the directory containing this file
    kernel_dir = os.path.dirname(os.path.abspath(__file__))
    kernelspec_dir = os.path.join(kernel_dir, 'kernelspec')
    
    # Check if kernelspec directory exists
    if not os.path.isdir(kernelspec_dir):
        print(f"Error: kernelspec directory not found at {kernelspec_dir}", file=sys.stderr)
        return 1
        
    # Install the kernel spec
    kernel_spec_manager = KernelSpecManager()
    
    try:
        dest = kernel_spec_manager.install_kernel_spec(
            kernelspec_dir,
            kernel_name='agent_client',
            user=user,
            prefix=prefix
        )
        print(f"Installed kernelspec agent_client in {dest}")
        return 0
    except Exception as e:
        print(f"Error installing kernel spec: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for the installation script."""
    parser = argparse.ArgumentParser(
        description='Install the Agent Client Protocol kernel spec'
    )
    parser.add_argument(
        '--user',
        action='store_true',
        help='Install to the per-user kernel registry'
    )
    parser.add_argument(
        '--sys-prefix',
        action='store_true',
        help='Install to sys.prefix (e.g. a virtualenv or conda env)'
    )
    parser.add_argument(
        '--prefix',
        help='Install to the given prefix'
    )
    
    args = parser.parse_args()
    
    if args.sys_prefix:
        prefix = sys.prefix
        user = False
    elif args.prefix:
        prefix = args.prefix
        user = False
    else:
        prefix = None
        user = args.user or True  # Default to user install
        
    return install_kernel_spec(user=user, prefix=prefix)


if __name__ == '__main__':
    sys.exit(main())
