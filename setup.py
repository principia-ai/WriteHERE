#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="writehere",
    version="0.1.0",
    author="WriteHERE Team",
    author_email="",
    description="Heterogeneous Recursive Planning based Open Writing Project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Digidai/WriteHERE",
    project_urls={
        "Bug Tracker": "https://github.com/Digidai/WriteHERE/issues",
        "Documentation": "https://writehere.site",
        "Source Code": "https://github.com/Digidai/WriteHERE",
    },
    packages=find_packages(exclude=["tests", "tests.*", "frontend", "backend"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "writehere=recursive.engine:main",
        ],
    },
)
