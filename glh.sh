#!/bin/bash

# Wrapper script for GitLab Helper.py

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "Python could not be found. Please install Python to continue."
    exit
fi

# Run the Python script with any arguments passed to this shell script
python glh.py "$@"