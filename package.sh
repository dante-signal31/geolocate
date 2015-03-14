#!/usr/bin/env bash

echo "Creating sdist package..."
python setup.py sdist
echo " "
echo "Creating wheel package..."
pip wheel --no-index --no-deps --wheel-dir dist dist/*.tar.gz
