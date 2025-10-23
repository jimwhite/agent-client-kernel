"""
Setup script for Agent Client Protocol Jupyter Kernel
"""

from setuptools import setup
import os.path

PKGNAME = 'agentclientkernel'
GITHUB_URL = 'https://github.com/jimwhite/agent-client-kernel'

pkg = __import__(PKGNAME)

with open('README.md') as f:
    readme = f.read()

setup_args = dict(
    name=PKGNAME,
    version=pkg.__version__,
    description='A Jupyter Kernel for Agent Client Protocol',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    url=GITHUB_URL,
    download_url=GITHUB_URL + '/tarball/v' + pkg.__version__,
    author='Jim White',
    author_email='jim@jimwhite.net',
    
    packages=[PKGNAME],
    install_requires=[
        "setuptools",
        "ipykernel >= 4.0",
        "jupyter-client >= 4.0",
        "agent-client-protocol >= 0.4.0"
    ],
    
    entry_points={
        'console_scripts': [
            'jupyter-agentclientkernel = agentclientkernel.__main__:main',
        ]
    },
    
    include_package_data=False,
    package_data={
        PKGNAME: ['resources/*.png']
    },
    
    keywords=['ACP', 'agent', 'IPython', 'Jupyter', 'kernel'],
    classifiers=[
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.10',
)

if __name__ == '__main__':
    setup(**setup_args)
