#!/usr/bin/env python3
"""Setup script for dynamic_baml package."""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    requirements = []
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

setup(
    name="dynamic_baml",
    version="0.1.0",
    author="Dynamic BAML Team",
    author_email="contact@dynamic-baml.com",
    description="A Python library for structured data extraction from text using Large Language Models with dynamically generated schemas",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/roboalchemist/dynamic-baml",
    project_urls={
        "Bug Tracker": "https://github.com/roboalchemist/dynamic-baml/issues",
        "Documentation": "https://dynamic-baml.readthedocs.io/",
        "Source Code": "https://github.com/roboalchemist/dynamic-baml",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-timeout>=2.1.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    include_package_data=True,
    package_data={
        "dynamic_baml": ["py.typed", "baml/*.baml", "baml/*.toml", "baml/*.py"],
    },
    entry_points={
        "console_scripts": [
            "dynamic-baml=dynamic_baml.cli:main",
        ],
    },
    keywords="llm, baml, data extraction, nlp, ai, machine learning, text processing",
    zip_safe=False,
) 