from setuptools import setup, find_packages
import os

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "MkDocs plugin to add 'Copy to LLM' buttons to documentation"

setup(
    name="mkdocs-copy-to-llm",
    version="0.1.0",
    author="Leonardo Custodio",
    author_email="leonardo@custodio.me",
    description="MkDocs plugin to add 'Copy to LLM' buttons to documentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonardocustodio/mkdocs-copy-to-llm",
    packages=find_packages(),
    package_data={
        "mkdocs_copy_to_llm": [
            "assets/js/*.js",
            "assets/css/*.css"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mkdocs>=1.2"
    ],
    entry_points={
        "mkdocs.plugins": [
            "copy-to-llm = mkdocs_copy_to_llm.plugin:CopyToLLMPlugin"
        ]
    },
)