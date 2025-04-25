#!/bin/bash

# Test script for deployment scenarios

# Test installing dependencies
echo "Testing: Installing dependencies"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# Test running the application
echo "Testing: Running the application"
python -m cacts
if [ $? -ne 0 ]; then
    echo "Failed to run the application"
    exit 1
fi

# Test verifying the application's output and behavior
echo "Testing: Verifying the application's output and behavior"
output=$(python -m cacts)
expected_output="CACTS: Cmake Application Configurable Testing System"
if [[ "$output" != *"$expected_output"* ]]; then
    echo "Application output verification failed"
    exit 1
fi

echo "All deployment tests passed"
exit 0
