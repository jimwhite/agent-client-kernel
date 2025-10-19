"""Setup script for agent-client-kernel."""

from setuptools import setup, find_packages
import os
import re

# Read the version from __init__.py
def get_version():
    with open(os.path.join('agent_client_kernel', '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                return re.search(r"'([^']+)'", line).group(1)
    raise RuntimeError('Version not found')

# Read the long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='agent-client-kernel',
    version=get_version(),
    description='A Jupyter kernel for Zed Agent Client Protocol',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jim White',
    license='GPL-3.0',
    url='https://github.com/jimwhite/agent-client-kernel',
    packages=find_packages(),
    install_requires=[
        'ipykernel>=6.0.0',
        'jupyter-client>=7.0.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Jupyter',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    package_data={
        'agent_client_kernel': ['kernelspec/*'],
    },
    entry_points={
        'console_scripts': [
            'agent-client-kernel=agent_client_kernel.install:main',
        ],
    },
)
