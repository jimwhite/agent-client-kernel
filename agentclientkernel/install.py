"""
Kernel installation utilities
"""

import sys
import os
import json
import io
import pkgutil

from jupyter_client.kernelspecapp import InstallKernelSpec, RemoveKernelSpec
from IPython.utils.tempdir import TemporaryDirectory

from . import __version__, KERNEL_NAME, DISPLAY_NAME


MODULEDIR = os.path.dirname(__file__)
PKGNAME = os.path.basename(MODULEDIR)


# The kernel spec JSON
kernel_json = {
    "argv": [sys.executable,
             "-m", PKGNAME,
             "-f", "{connection_file}"],
    "display_name": DISPLAY_NAME,
    "name": KERNEL_NAME,
    "language": "agent"
}


def copyresource(resource, filename, destdir):
    """Copy a resource file to a destination"""
    data = pkgutil.get_data(resource, os.path.join('resources', filename))
    with io.open(os.path.join(destdir, filename), 'wb') as fp:
        fp.write(data)


def install_kernel_resources(destdir, resource=PKGNAME, files=None):
    """Copy the resource files to the kernelspec folder"""
    if files is None:
        files = ['logo-64x64.png', 'logo-32x32.png']
    for filename in files:
        try:
            copyresource(resource, filename, destdir)
        except Exception as e:
            # Resource files are optional
            pass


class ACPInstall(InstallKernelSpec):
    """Install the ACP kernel"""
    
    version = __version__
    kernel_name = KERNEL_NAME
    description = '''Install the Agent Client Protocol Kernel'''
    
    def parse_command_line(self, argv):
        """Skip parent method and go for its ancestor"""
        super(InstallKernelSpec, self).parse_command_line(argv)
    
    def start(self):
        if self.user and self.prefix:
            self.exit("Can't specify both user and prefix. Please choose one.")
        
        self.log.info('Installing Agent Client Protocol kernel')
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)
            
            # Write kernel.json
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            
            # Copy logo resources
            install_kernel_resources(td, resource=PKGNAME)
            
            # Install the kernel spec
            self.log.info('Installing kernel spec')
            self.sourcedir = td
            install_dir = self.kernel_spec_manager.install_kernel_spec(
                td,
                kernel_name=self.kernel_name,
                user=self.user,
                prefix=self.prefix,
                replace=self.replace,
            )
        
        self.log.info("Installed into %s", install_dir)


class ACPRemove(RemoveKernelSpec):
    """Remove the ACP kernel"""
    
    spec_names = [KERNEL_NAME]
    description = '''Remove the Agent Client Protocol Kernel'''
    
    def parse_command_line(self, argv):
        """Skip parent method and go for its ancestor"""
        super(RemoveKernelSpec, self).parse_command_line(argv)
