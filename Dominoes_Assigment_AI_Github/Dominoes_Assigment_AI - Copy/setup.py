from setuptools import setup, find_packages

setup(
    name="domino_ai",
    version="0.1",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'pyyaml',
        'numpy',  # Also required for the AI strategies
        'colorama',  # Required for CLI color output
    ],
)