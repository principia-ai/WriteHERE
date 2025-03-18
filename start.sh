#!/bin/bash

# Function to display messages
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Function to display error messages
error_log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] $1" >&2
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

# Function to kill process using a specific port
kill_process_on_port() {
  local port=$1
  local force=$2
  
  log "Checking for processes using port $port..."
  
  local pid
  if command -v lsof >/dev/null 2>&1; then
    pid=$(lsof -ti:$port -sTCP:LISTEN)
  elif command -v netstat >/dev/null 2>&1; then
    pid=$(netstat -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
  fi
  
  if [ -n "$pid" ]; then
    log "Found process with PID $pid using port $port"
    local kill_cmd="kill"
    if [ "$force" = "force" ]; then
      kill_cmd="kill -9"
    fi
    
    log "Attempting to stop process with PID $pid..."
    eval "$kill_cmd $pid"
    
    # Check if process was killed
    sleep 1
    if ! ps -p $pid > /dev/null 2>&1; then
      log "Process with PID $pid successfully stopped"
      return 0
    else
      if [ "$force" != "force" ]; then
        log "Failed to stop process with PID $pid, trying force kill..."
        kill_process_on_port $port "force"
      else
        error_log "Failed to stop process with PID $pid even with force kill"
        return 1
      fi
    fi
  else
    log "No process found using port $port"
    return 0
  fi
}

# Function to cleanup ports at startup
cleanup_ports() {
  log "Cleaning up ports before starting..."
  
  # Clean port 5001 (backend)
  if is_port_in_use 5001; then
    log "Port 5001 is in use. Attempting to free it..."
    kill_process_on_port 5001
    sleep 1
    if is_port_in_use 5001; then
      error_log "Could not free port 5001. Please check manually."
      exit 1
    else
      log "Successfully freed port 5001"
    fi
  else
    log "Port 5001 is free"
  fi
  
  # Clean port 3000 (frontend)
  if is_port_in_use 3000; then
    log "Port 3000 is in use. Attempting to free it..."
    kill_process_on_port 3000
    sleep 1
    if is_port_in_use 3000; then
      error_log "Could not free port 3000. Please check manually."
      exit 1
    else
      log "Successfully freed port 3000"
    fi
  else
    log "Port 3000 is free"
  fi
}

# Function to cleanup when shutting down
cleanup_before_exit() {
  log "Shutting down..."
  
  # Kill the specific processes we started
  if [ -n "$backend_pid" ]; then
    log "Stopping backend server (PID: $backend_pid)..."
    kill $backend_pid 2>/dev/null || kill -9 $backend_pid 2>/dev/null
  fi
  
  if [ -n "$frontend_pid" ]; then
    log "Stopping frontend server (PID: $frontend_pid)..."
    kill $frontend_pid 2>/dev/null || kill -9 $frontend_pid 2>/dev/null
  fi
  
  # Additionally cleanup any processes that might still be using our ports
  log "Performing final port cleanup..."
  kill_process_on_port 5001
  kill_process_on_port 3000
  
  log "WriteHERE stopped."
  exit 0
}

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

# Function to start the backend server
start_backend() {
  log "Starting backend server..."
  
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
  log "Starting backend server on port 5001..."
  cd backend
  python server.py &
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
  python test_api.py
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
  log "Starting frontend server on port 3000..."
  cd frontend
  npm start &
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
log "  - Backend server: http://localhost:5001"
log "  - Frontend app:   http://localhost:3000"
log "  - Press Ctrl+C to stop both servers"
log "==============================="

# Open the browser automatically if possible
if command -v open >/dev/null 2>&1; then
  log "Opening browser..."
  open http://localhost:3000
elif command -v xdg-open >/dev/null 2>&1; then
  log "Opening browser..."
  xdg-open http://localhost:3000
elif command -v start >/dev/null 2>&1; then
  log "Opening browser..."
  start http://localhost:3000
fi

# Wait for user to stop the servers
wait