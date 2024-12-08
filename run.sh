#!/bin/bash

# Function to check if port is in use
check_port() {
    if lsof -i :8080 > /dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill any existing Python processes
echo "Stopping any existing Python processes..."
pkill -f "python3 backend/app.py"

# Wait a moment for processes to stop
sleep 2

# Check if port is still in use
if check_port; then
    echo "Error: Port 8080 is still in use. Please check for other processes using this port."
    echo "You can use: lsof -i :8080"
    exit 1
fi

# Start the backend server
echo "Starting the backend server..."
cd backend || exit 1

# Run with explicit python3 and error handling
if ! python3 app.py; then
    echo "Error: Failed to start the backend server"
    exit 1
fi

# Note: Server is now running in the foreground
# Access instructions will be shown by Flask
