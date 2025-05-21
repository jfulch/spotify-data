#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt