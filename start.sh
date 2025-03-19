#!/bin/bash

# Function to display messages
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Function to display error messages
error_log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] $1" >&2
}

# Default port values
BACKEND_PORT=5001
FRONTEND_PORT=3000

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --backend-port)
      BACKEND_PORT="$2"
      shift 2
      ;;
    --frontend-port)
      FRONTEND_PORT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Check if required API keys are set
check_api_keys() {
  api_key_env_file="recursive/api_key.env"
  if [ -f "$api_key_env_file" ]; then
    log "API key file exists: $api_key_env_file"
  else
    log "WARNING: API key file does not exist at $api_key_env_file"
    log "You'll need to provide API keys in the web interface."
    
    # Create an empty API key file
    touch "$api_key_env_file"
  fi
}

# Check if a port is in use
is_port_in_use() {
  if command -v nc >/dev/null 2>&1; then
    nc -z localhost $1 >/dev/null 2>&1
    return $?
  elif command -v lsof >/dev/null 2>&1; then
    lsof -i:$1 >/dev/null 2>&1
    return $?
  else
    # Default to assuming port is free if we can't check
    return 1
  fi
}

# Function to start the backend server
start_backend() {
  log "Starting backend server..."
  
  # Check if configured port is already in use
  if is_port_in_use $BACKEND_PORT; then
    error_log "Port $BACKEND_PORT is already in use. The backend server may already be running."
    error_log "Please stop any services using port $BACKEND_PORT or specify a different port with --backend-port."
    exit 1
  fi
  
  # Make sure Python virtual environment exists
  if [ ! -d "venv" ]; then
    log "Creating Python virtual environment..."
    python -m venv venv || python3 -m venv venv
    if [ $? -ne 0 ]; then
      error_log "Failed to create Python virtual environment."
      exit 1
    fi
  fi
  
  # Activate virtual environment
  source venv/bin/activate
  if [ $? -ne 0 ]; then
    error_log "Failed to activate Python virtual environment."
    exit 1
  fi
  
  # Install backend dependencies
  log "Installing backend dependencies..."
  pip install -v -e . || pip3 install -v -e .
  if [ $? -ne 0 ]; then
    error_log "Failed to install main package dependencies."
    exit 1
  fi
  
  pip install -r backend/requirements.txt || pip3 install -r backend/requirements.txt
  if [ $? -ne 0 ]; then
    error_log "Failed to install backend requirements."
    exit 1
  fi
  
  # Start backend server
  log "Starting backend server on port $BACKEND_PORT..."
  cd backend
  python server.py --port $BACKEND_PORT &
  backend_pid=$!
  cd ..
  
  # Check if backend server started successfully
  sleep 2
  if ! ps -p $backend_pid > /dev/null; then
    error_log "Backend server failed to start."
    exit 1
  fi
  
  log "Backend server started with PID: $backend_pid"
  
  # Test the API connection
  log "Testing API connection..."
  cd backend
  python test_api.py --port $BACKEND_PORT
  api_test_result=$?
  cd ..
  
  if [ $api_test_result -ne 0 ]; then
    error_log "API connection test failed. The backend server may not be running properly."
    log "Continuing startup process, but be aware there may be connectivity issues."
  fi
}

# Function to start the frontend
start_frontend() {
  log "Starting frontend..."
  
  # Check if configured port is already in use
  if is_port_in_use $FRONTEND_PORT; then
    error_log "Port $FRONTEND_PORT is already in use. The frontend server may already be running."
    error_log "Please stop any services using port $FRONTEND_PORT or specify a different port with --frontend-port."
    exit 1
  fi
  
  # Install frontend dependencies if needed
  if [ ! -d "frontend/node_modules" ]; then
    log "Installing frontend dependencies..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
      error_log "Failed to install frontend dependencies."
      exit 1
    fi
    cd ..
  fi
  
  # Start frontend development server
  log "Starting frontend server on port $FRONTEND_PORT..."
  cd frontend
  PORT=$FRONTEND_PORT REACT_APP_BACKEND_PORT=$BACKEND_PORT npm start &
  frontend_pid=$!
  cd ..
  
  # Check if frontend server started successfully
  sleep 5
  if ! ps -p $frontend_pid > /dev/null; then
    error_log "Frontend server failed to start."
    exit 1
  fi
  
  log "Frontend started with PID: $frontend_pid"
}

# Set up cleanup trap for Ctrl+C and other termination
trap cleanup_before_exit INT TERM

# Main execution
log "Starting WriteHERE application..."
log "==============================="

# First cleanup any existing processes using our ports
cleanup_ports

# Ensure we have API keys or notify the user
check_api_keys

# Start backend first
start_backend

# Allow backend time to initialize
log "Waiting for backend to initialize..."
sleep 3

# Start frontend next
start_frontend

log "==============================="
log "WriteHERE is now running!"
log "  - Backend server: http://localhost:$BACKEND_PORT"
log "  - Frontend app:   http://localhost:$FRONTEND_PORT"
log "  - Press Ctrl+C to stop both servers"
log "==============================="

# Open the browser automatically if possible
if command -v open >/dev/null 2>&1; then
  log "Opening browser..."
  open http://localhost:$FRONTEND_PORT
elif command -v xdg-open >/dev/null 2>&1; then
  log "Opening browser..."
  xdg-open http://localhost:$FRONTEND_PORT
elif command -v start >/dev/null 2>&1; then
  log "Opening browser..."
  start http://localhost:$FRONTEND_PORT
fi

# Handle graceful shutdown
trap 'log "Shutting down..."; kill $backend_pid $frontend_pid 2>/dev/null; log "WriteHERE stopped."; exit 0' INT TERM

# Wait for user to stop the servers
wait