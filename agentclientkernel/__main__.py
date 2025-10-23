"""
Entry point for the Agent Client Protocol kernel
"""

from ipykernel.kernelapp import IPKernelApp
from traitlets import Dict


class ACPKernelApp(IPKernelApp):
    """The main kernel application"""
    
    from .kernel import ACPKernel
    from .install import ACPInstall, ACPRemove
    
    kernel_class = ACPKernel
    
    # Override subcommands to add install/remove commands
    subcommands = Dict({
        'install': (ACPInstall, 
                    ACPInstall.description.splitlines()[0]),
        'remove': (ACPRemove,
                   ACPRemove.description.splitlines()[0]),
    })


def main():
    """Entry point for the kernel"""
    ACPKernelApp.launch_instance()


if __name__ == '__main__':
    main()
