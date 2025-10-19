"""Entry point for the kernel."""

from ipykernel.kernelapp import IPKernelApp
from .kernel import AgentClientKernel

if __name__ == '__main__':
    IPKernelApp.launch_instance(kernel_class=AgentClientKernel)
