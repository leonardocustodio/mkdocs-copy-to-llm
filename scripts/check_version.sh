#!/bin/bash
# Check version consistency between pyproject.toml and __init__.py

VER1=$(grep "^version =" pyproject.toml | head -1 | cut -d'"' -f2)
VER2=$(grep "__version__" mkdocs_copy_to_llm/__init__.py | cut -d'"' -f2)

if [ "$VER1" != "$VER2" ]; then
    echo "Version mismatch: pyproject.toml=$VER1, __init__.py=$VER2"
    exit 1
fi
