from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import subprocess
import uuid
import tempfile
import threading
import time
import shutil
import re
import signal
import argparse
from pathlib import Path
from datetime import datetime

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Backend server for WriteHERE application')
parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
args = parser.parse_args()

app = Flask(__name__)
# Enable CORS with more specific options
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# Initialize Socket.IO with broader CORS settings for development
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    async_mode='threading',
                    logger=False, # disable logger
                    engineio_logger=False)

# Storage for task status and results
task_storage = {}
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def reload_task_storage():
    """Reload task storage from the file system"""
    global task_storage
    
    # Iterate through all folders in the results directory
    for task_id in os.listdir(RESULTS_DIR):
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if not os.path.isdir(task_dir):
            continue
            
        # Check if this is a completed task with results
        result_file = os.path.join(task_dir, 'result.jsonl')
        done_file = os.path.join(task_dir, 'done.txt')
        
        if os.path.exists(result_file):
            # Add task to storage if not already there
            if task_id not in task_storage:
                creation_time = os.path.getctime(task_dir)
                task_storage[task_id] = {
                    "status": "completed" if os.path.exists(done_file) else "running",
                    "start_time": creation_time
                }
                
                # Try to extract model information from run.sh
                run_sh_file = os.path.join(task_dir, 'run.sh')
                if os.path.exists(run_sh_file):
                    try:
                        with open(run_sh_file, 'r') as f:
                            run_script = f.read()
                            # Extract model name from command line arguments
                            model_match = run_script.split("--model ")[1].split(" ")[0] if "--model " in run_script else None
                            if model_match:
                                task_storage[task_id]["model"] = model_match
                            
                            # Check if it's a report with search
                            if "--engine-backend " in run_script:
                                engine_backend = run_script.split("--engine-backend ")[1].split(" ")[0]
                                if engine_backend != "none":
                                    task_storage[task_id]["search_engine"] = engine_backend
                    except Exception as e:
                        print(f"Error extracting model info from run.sh for {task_id}: {str(e)}")
                
                # Load result if available
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        task_storage[task_id]["result"] = result_data.get("result", "No result available")
                except Exception as e:
                    print(f"Error loading result file for {task_id}: {str(e)}")
                    task_storage[task_id]["error"] = f"Failed to load output file: {str(e)}"

# Load existing tasks on startup
reload_task_storage()

def run_story_generation(task_id, prompt, model, api_keys):
    """
    Run the story generation script as a subprocess
    """
    task_dir = os.path.join(RESULTS_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    # Create a records directory for nodes.json
    records_dir = os.path.join(task_dir, 'records')
    os.makedirs(records_dir, exist_ok=True)
    
    # Create a temporary input file with the prompt
    input_file = os.path.join(task_dir, 'input.jsonl')
    with open(input_file, 'w') as f:
        json.dump({
            "id": task_id,
            "field": "inputs",
            "value": prompt,
            "ori": {"example_id": task_id, "inputs": prompt, "subset": "user"}
        }, f)
        f.write('\n')
    
    output_file = os.path.join(task_dir, 'result.jsonl')
    done_file = os.path.join(task_dir, 'done.txt')
    nodes_file = os.path.join(records_dir, 'nodes.json')
    
    # Create environment file with API keys
    env_file = os.path.join(task_dir, 'api_key.env')
    with open(env_file, 'w') as f:
        if 'openai' in api_keys and api_keys['openai']:
            f.write(f"OPENAI={api_keys['openai']}\n")
        if 'claude' in api_keys and api_keys['claude']:
            f.write(f"CLAUDE={api_keys['claude']}\n")
        if 'serpapi' in api_keys and api_keys['serpapi']:
            f.write(f"SERPAPI={api_keys['serpapi']}\n")
    
    # Create a script to run the engine with the appropriate environment
    script_path = os.path.join(task_dir, 'run.sh')
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
        cd {os.path.abspath(os.path.join(os.path.dirname(__file__), '../recursive'))}
        source {env_file}
        export TASK_ENV_FILE={env_file}
        python engine.py --filename {input_file} --output-filename {output_file} --done-flag-file {done_file} --model {model} --mode story --nodes-json-file {nodes_file}
        """)
    
    os.chmod(script_path, 0o755)
    
    # Update task status to "running"
    task_storage[task_id] = {
        "status": "running", 
        "start_time": time.time(),
        "model": model
    }
    
    # Start task progress monitoring in a background thread
    monitoring_thread = threading.Thread(
        target=monitor_task_progress,
        args=(task_id, records_dir)
    )
    monitoring_thread.daemon = True
    monitoring_thread.start()
    
    try:
        # Run the script
        process = subprocess.Popen(['/bin/bash', script_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        # Store the process object in task_storage for later termination
        task_storage[task_id]["process"] = process
        stdout, stderr = process.communicate()
        
        # Check if the process completed successfully
        if process.returncode == 0:
            task_storage[task_id]["status"] = "completed"
            # Store the result if available
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    result_data = json.load(f)
                    task_storage[task_id]["result"] = result_data.get("result", "No result available")
            else:
                task_storage[task_id]["status"] = "error"
                task_storage[task_id]["error"] = "Output file not generated"
        else:
            task_storage[task_id]["status"] = "error"
            task_storage[task_id]["error"] = stderr.decode('utf-8')
    except Exception as e:
        task_storage[task_id]["status"] = "error"
        task_storage[task_id]["error"] = str(e)

def run_report_generation(task_id, prompt, model, enable_search, search_engine, api_keys):
    """
    Run the report generation script as a subprocess
    """
    task_dir = os.path.join(RESULTS_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    # Create a records directory for nodes.json
    records_dir = os.path.join(task_dir, 'records')
    os.makedirs(records_dir, exist_ok=True)
    
    # Create a temporary input file with the prompt
    input_file = os.path.join(task_dir, 'input.jsonl')
    with open(input_file, 'w') as f:
        json.dump({
            "topic": "",
            "intent": "",
            "domain": "",
            "id": task_id,
            "prompt": prompt
        }, f)
        f.write('\n')
    
    output_file = os.path.join(task_dir, 'result.jsonl')
    done_file = os.path.join(task_dir, 'done.txt')
    nodes_file = os.path.join(records_dir, 'nodes.json')
    
    # Create environment file with API keys
    env_file = os.path.join(task_dir, 'api_key.env')
    with open(env_file, 'w') as f:
        if 'openai' in api_keys and api_keys['openai']:
            f.write(f"OPENAI={api_keys['openai']}\n")
        if 'claude' in api_keys and api_keys['claude']:
            f.write(f"CLAUDE={api_keys['claude']}\n")
        if 'serpapi' in api_keys and api_keys['serpapi']:
            f.write(f"SERPAPI={api_keys['serpapi']}\n")
    
    # Create a script to run the engine with the appropriate environment
    script_path = os.path.join(task_dir, 'run.sh')
    engine_backend = search_engine if enable_search else "none"
    
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
        cd {os.path.abspath(os.path.join(os.path.dirname(__file__), '../recursive'))}
        source {env_file}
        export TASK_ENV_FILE={env_file}
        python engine.py --filename {input_file} --output-filename {output_file} --done-flag-file {done_file} --model {model} --engine-backend {engine_backend} --mode report --nodes-json-file {nodes_file}
        """)
    
    os.chmod(script_path, 0o755)
    
    # Update task status to "running"
    task_storage[task_id] = {
        "status": "running", 
        "start_time": time.time(),
        "model": model,
        "search_engine": engine_backend if enable_search else None
    }
    
    # Start task progress monitoring in a background thread
    monitoring_thread = threading.Thread(
        target=monitor_task_progress,
        args=(task_id, records_dir)
    )
    monitoring_thread.daemon = True
    monitoring_thread.start()
    
    try:
        # Run the script
        process = subprocess.Popen(['/bin/bash', script_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        # Store the process object in task_storage for later termination
        task_storage[task_id]["process"] = process
        stdout, stderr = process.communicate()
        
        # Check if the process completed successfully
        if process.returncode == 0:
            task_storage[task_id]["status"] = "completed"
            # Store the result if available
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    result_data = json.load(f)
                    task_storage[task_id]["result"] = result_data.get("result", "No result available")
            else:
                task_storage[task_id]["status"] = "error"
                task_storage[task_id]["error"] = "Output file not generated"
        else:
            task_storage[task_id]["status"] = "error"
            task_storage[task_id]["error"] = stderr.decode('utf-8')
    except Exception as e:
        task_storage[task_id]["status"] = "error"
        task_storage[task_id]["error"] = str(e)

@app.route('/api/generate-story', methods=['POST'])
def api_generate_story():
    data = request.json
    
    # Validate request
    required_fields = ['prompt', 'model', 'apiKeys']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Generate a unique task ID
    task_id = f"story-{uuid.uuid4()}"
    
    # Start the generation in a background thread
    thread = threading.Thread(
        target=run_story_generation,
        args=(task_id, data['prompt'], data['model'], data['apiKeys'])
    )
    thread.start()
    
    return jsonify({
        "taskId": task_id,
        "status": "started"
    })

@app.route('/api/generate-report', methods=['POST'])
def api_generate_report():
    data = request.json
    
    # Validate request
    required_fields = ['prompt', 'model', 'apiKeys']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Set defaults
    enable_search = data.get('enableSearch', True)
    search_engine = data.get('searchEngine', 'google')
    
    # Generate a unique task ID
    task_id = f"report-{uuid.uuid4()}"
    
    # Start the generation in a background thread
    thread = threading.Thread(
        target=run_report_generation,
        args=(task_id, data['prompt'], data['model'], enable_search, search_engine, data['apiKeys'])
    )
    thread.start()
    
    return jsonify({
        "taskId": task_id,
        "status": "started"
    })

@app.route('/api/status/<task_id>', methods=['GET'])
def api_get_status(task_id):
    # If task is not in memory, try to load it
    if task_id not in task_storage:
        task_dir = os.path.join(RESULTS_DIR, task_id)
        print('debug')
        if os.path.isdir(task_dir):
            # Load task into memory
            result_file = os.path.join(task_dir, 'result.jsonl')
            done_file = os.path.join(task_dir, 'done.txt')
            
            if os.path.exists(result_file):
                creation_time = os.path.getctime(task_dir)
                task_storage[task_id] = {
                    "status": "completed" if os.path.exists(done_file) else "running",
                    "start_time": creation_time
                }
                
                # Load result if available
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        task_storage[task_id]["result"] = result_data.get("result", "No result available")
                except Exception as e:
                    print(f"Error loading result file for {task_id}: {str(e)}")
                    task_storage[task_id]["error"] = f"Failed to load output file: {str(e)}"
            else:
                return jsonify({"error": "Task not found or incomplete"}), 404
        else:
            return jsonify({"error": "Task not found"}), 404
    
    task = task_storage[task_id]
    
    # Check if we need to update status from the done file
    task_dir = os.path.join(RESULTS_DIR, task_id)
    done_file = os.path.join(task_dir, 'done.txt')
    
    if task["status"] == "running" and os.path.exists(done_file):
        task["status"] = "completed"
    
    return jsonify({
        "taskId": task_id,
        "status": task["status"],
        "error": task.get("error"),
        "elapsedTime": time.time() - task["start_time"],
        "model": task.get("model", "unknown"),
        "searchEngine": task.get("search_engine")
    })

@app.route('/api/result/<task_id>', methods=['GET'])
def api_get_result(task_id):
    # If task is not in memory, try to load it
    if task_id not in task_storage:
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if os.path.isdir(task_dir):
            # Load task into memory
            result_file = os.path.join(task_dir, 'result.jsonl')
            done_file = os.path.join(task_dir, 'done.txt')
            
            if os.path.exists(result_file):
                creation_time = os.path.getctime(task_dir)
                task_storage[task_id] = {
                    "status": "completed" if os.path.exists(done_file) else "running",
                    "start_time": creation_time
                }
                
                # Load result if available
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        task_storage[task_id]["result"] = result_data.get("result", "No result available")
                except Exception as e:
                    print(f"Error loading result file for {task_id}: {str(e)}")
                    task_storage[task_id]["error"] = f"Failed to load output file: {str(e)}"
                    return jsonify({"error": f"Failed to load output file: {str(e)}"}), 500
            else:
                return jsonify({"error": "Task result file not found"}), 404
        else:
            return jsonify({"error": "Task not found"}), 404
    
    result_md_dir = os.path.join(RESULTS_DIR, 'records', task_id, 'report.md')
    task = task_storage[task_id]
    
    # We'll allow getting results even if status is not completed as long as we have the result data
    if "result" not in task:
        # Check if the result.md file exists
        if not os.path.exists(result_md_dir):
            return jsonify({"error": "Task result not available"}), 400
        else:
            with open(result_md_dir, 'r') as f:
                task["result"] = f.read()
        # Check if the result.md file exists
        if not os.path.exists(result_md_dir):
            return jsonify({"error": "Task result not available"}), 400
        else:
            with open(result_md_dir, 'r') as f:
                task["result"] = f.read()
    
    return jsonify({
        "taskId": task_id,
        "result": task.get("result", "No result available"),
        "model": task.get("model", "unknown"),
        "searchEngine": task.get("search_engine")
    })


def transform_node_to_graph(node, seen_nodes=None, root=False):
    """
    Transform a node from the internal format to the format expected by the frontend
    Based on the display logic in display.py
    """
    if seen_nodes is None:
        seen_nodes = set()
        
    # Get the base node data
    task_info = node.get("task_info", {})
    
    # Use nid for the ID field
    node_id = node.get("nid", "")
    
    # Skip if we've seen this node before (prevents duplication)
    if node_id in seen_nodes and not root:
        return None
    
    # Add this node to the set of seen nodes
    seen_nodes.add(node_id)
    
    # Get the node status
    status = node.get("status", "UNKNOWN")
    
    # Determine if this is an execute node
    is_execute_node = node.get("node_type") == "EXECUTE_NODE"
    
    transformed = {
        "id": node_id,
        "goal": task_info.get("goal", "Unknown"),
        "task_type": task_info.get("task_type", "unknown"),
        "status": status,
        "dependency": task_info.get("dependency", []),
        "sub_tasks": [],
        "node_type": node.get("node_type", "UNKNOWN"),
        "is_execute_node": is_execute_node,
    }
    
    # Add action information if available
    if "result" in node:
        # The node.result dictionary contains actions as keys
        # Include both the latest action and all actions
        actions = []
        latest_action_name = None
        latest_action_result = None
        
        for action_name, action_data in node.get("result", {}).items():
            raw_result = action_data.get("result", {})
            action_result = raw_result.get("result", "") if isinstance(raw_result, dict) else raw_result
            action_time = action_data.get("time", "")
            
            actions.append({
                "name": action_name,
                "result": action_result,
                "time": action_time
            })
            
            # Track the latest action by time
            if not latest_action_name or action_time > node.get("result", {}).get(latest_action_name, {}).get("time", ""):
                latest_action_name = action_name
                latest_action_result = action_result
                
        if actions:
            transformed["actions"] = actions
        
        if latest_action_name:
            transformed["latest_action"] = {
                "name": latest_action_name,
                "result": latest_action_result
            }
    
    # For task graph visualization, we need to collect and flatten all subtasks
    # from the node hierarchy
    def collect_subtasks(current_node, parent_transformed):
        """Recursively collect all subtasks from a node and its children"""
        if not current_node:
            return
            
        # Get the inner graph of the current node
        inner = current_node.get("inner_graph", {})
        if not inner or "topological_task_queue" not in inner:
            return
            
        # Get and sort tasks by ID
        tasks = inner.get("topological_task_queue", [])
        sorted_tasks = sorted(
            tasks,
            key=lambda x: int(str(x.get("nid", "0")).split(".")[-1])
        )
        
        # Process each task
        for task in sorted_tasks:
            task_id = task.get("nid", "")
            
            # Skip duplicate nodes
            if task_id in seen_nodes and task_id != current_node.get("nid"):
                continue
                
            # Mark this node as seen
            seen_nodes.add(task_id)
            
            # Create the transformed task
            task_info = task.get("task_info", {})
            is_execute = task.get("node_type") == "EXECUTE_NODE"
            
            sub_task = {
                "id": task_id,
                "goal": task_info.get("goal", "Unknown"),
                "task_type": task_info.get("task_type", "unknown"),
                "status": task.get("status", "UNKNOWN"),
                "dependency": task_info.get("dependency", []),
                "sub_tasks": [],
                "node_type": task.get("node_type", "UNKNOWN"),
                "is_execute_node": is_execute
            }
            
            # Add action information if available
            if "result" in task:
                # The task.result dictionary contains actions as keys
                # Include both the latest action and all actions
                actions = []
                latest_action_name = None
                latest_action_result = None
                
                for action_name, action_data in task.get("result", {}).items():
                    raw_result = action_data.get("result", {})
                    action_result = raw_result.get("result", "") if isinstance(raw_result, dict) else raw_result
                    
                    actions.append({
                        "name": action_name,
                        "result": action_result,
                        "time": action_time
                    })
                    
                    # Track the latest action by time
                    if not latest_action_name or action_time > task.get("result", {}).get(latest_action_name, {}).get("time", ""):
                        latest_action_name = action_name
                        latest_action_result = action_result
                        
                if actions:
                    sub_task["actions"] = actions
                
                if latest_action_name:
                    sub_task["latest_action"] = {
                        "name": latest_action_name,
                        "result": latest_action_result
                    }
            
            # Add to parent's subtasks
            parent_transformed["sub_tasks"].append(sub_task)
            
            # For task graph visualization, we don't skip execute nodes
            # Instead we process their subtasks but mark them specially
            collect_subtasks(task, sub_task)
    
    # Start collecting subtasks from this node
    collect_subtasks(node, transformed)
    
    return transformed

@app.route('/api/task-graph/<task_id>', methods=['GET'])
def api_get_task_graph(task_id):
    """
    Get the task graph data (nodes and edges) for a specific task
    """
    # Check if the task directory exists
    task_dir = os.path.join(RESULTS_DIR, task_id)
    if not os.path.isdir(task_dir):
        return jsonify({"error": "Task not found"}), 404
    
    # Possible locations for the nodes.json file
    nodes_paths = [
        os.path.join(task_dir, 'records', 'nodes.json'),
        os.path.join(RESULTS_DIR, 'records', task_id, 'nodes.json')
    ]
    
    nodes_file = None
    for path in nodes_paths:
        if os.path.exists(path):
            nodes_file = path
            break
    
    if not nodes_file:
        # Create a simple task graph if we can't find the real one
        
        # Get prompt from input file
        input_file = os.path.join(task_dir, 'input.jsonl')
        prompt = "Unknown task"
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r') as f:
                    input_data = json.load(f)
                    if 'value' in input_data:
                        prompt = input_data.get('value', '')
            except Exception as e:
                print(f"Error reading input file: {str(e)}")
        
        simple_graph = {
            "id": "",
            "goal": prompt,
            "task_type": "write",
            "status": "FINISH",
            "sub_tasks": [
                {
                    "id": "0",
                    "goal": "Task graph data not available",
                    "task_type": "think",
                    "status": "FINISH",
                    "sub_tasks": []
                }
            ]
        }
        
        return jsonify({
            "taskId": task_id,
            "taskGraph": simple_graph
        })
    
    try:
        with open(nodes_file, 'r') as f:
            nodes_data = json.load(f)
        
        # Transform the data to the format expected by the frontend
        transformed_graph = transform_node_to_graph(nodes_data, root=True)
        
        return jsonify({
            "taskId": task_id,
            "taskGraph": transformed_graph
        })
    except Exception as e:
        print(f"Error processing nodes.json: {str(e)}")
        return jsonify({"error": f"Failed to read task graph data: {str(e)}"}), 500

@app.route('/api/reload', methods=['POST'])
def api_reload_tasks():
    """Reload all tasks from the file system"""
    reload_task_storage()
    return jsonify({
        "status": "ok",
        "message": "Task storage reloaded",
        "taskCount": len(task_storage)
    })
    
@app.route('/api/stop-task/<task_id>', methods=['POST'])
def api_stop_task(task_id):
    """Stop a running task"""
    try:
        # Sanitize task_id to prevent path traversal
        if not re.match(r'^[a-zA-Z0-9_\-]+$', task_id):
            return jsonify({"status": "error", "error": "Invalid task ID format"}), 400
            
        # Check if task exists
        if task_id not in task_storage:
            return jsonify({"status": "error", "error": "Task not found"}), 404
            
        # Check if task is already completed or stopped
        if task_storage[task_id]["status"] in ["completed", "error", "stopped"]:
            return jsonify({
                "status": "ok",
                "message": f"Task {task_id} is already {task_storage[task_id]['status']}"
            })
        
          
        # Direct approach: Find the pid for the python engine.py process and kill it
        task_dir = os.path.join(RESULTS_DIR, task_id)

        # 1. Create a stop.txt file for the task to detect gracefully                                                 │ │
        stop_file = os.path.join(task_dir, 'stop.txt') 
        
        # First try to find the PID using ps command
        try:
            # For the specific task_id, find the python engine.py process
            cmd = f"ps -ef | grep '{task_id}' | grep 'engine.py' | grep -v grep | awk '{{print $2}}'"
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            
            if result:
                pid = int(result)
                print(f"Found Python engine.py process with PID {pid} for task {task_id}")
                
                # Kill the process and its children
                print(f"Killing process {pid} and its children")
                if os.name != 'nt':  # Unix/Linux/MacOS
                    # try:
                    #     # Try to kill process group first
                    #     os.killpg(os.getpgid(pid), signal.SIGKILL)
                    #     print(f"Sent SIGKILL to process group for PID {pid}")
                    # except Exception as group_err:
                    #     print(f"Error killing process group: {str(group_err)}")
                        
                    # Also try direct kill commands
                    os.system(f"kill -9 {pid}")
                    os.system(f"pkill -P {pid}")  # Kill all child processes
                    print(f"Used kill commands on PID {pid}")
                else:
                    # Windows
                    os.system(f"taskkill /F /PID {pid} /T")
                    print(f"Used taskkill on PID {pid}")
            else:
                print(f"Could not find Python engine.py process for task {task_id}")
                
                # Fall back to looking for the run.sh process
                cmd = f"ps -ef | grep '{task_dir}/run.sh' | grep -v grep | awk '{{print $2}}'"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                
                if result:
                    pid = int(result)
                    print(f"Found run.sh process with PID {pid} for task {task_id}")
                    
                    # Kill the process
                    if os.name != 'nt':
                        os.system(f"kill -9 {pid}")
                        # os.system(f"pkill -P {pid}")
                    else:
                        os.system(f"taskkill /F /PID {pid} /T")
                else:
                    print(f"Could not find run.sh process for task {task_id}")
                    
        except Exception as e:
            print(f"Error finding or killing processes for task {task_id}: {str(e)}")
            
            # As a last resort, try to kill any processes related to the task directory
            if os.name != 'nt':
                os.system(f"pkill -f '{task_dir}'")
                print(f"Attempted to kill any processes related to {task_dir}")
        
        # Create a done file to indicate the task is stopped
        with open(os.path.join(task_dir, 'done.txt'), 'w') as f:
            f.write("Stopped by user at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Update task status
        task_storage[task_id]["status"] = "stopped"
        
        # Set a result message for stopped tasks
        task_storage[task_id]["result"] = "Task was stopped by user request before completion."
        
        # Emit a socket message to notify the frontend
        socketio.emit('task_update', {
            'taskId': task_id,
            'status': 'stopped',
            'message': 'Task has been stopped by user request'
        })
        
        return jsonify({
            "status": "ok",
            "message": f"Task {task_id} has been stopped"
        })
    except Exception as e:
        app.logger.error(f"Error stopping task {task_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "error": f"Failed to stop task: {str(e)}"
        }), 500

@app.route('/api/delete-task/<task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete a previously generated task and its associated files"""
    try:
        # Sanitize task_id to prevent path traversal
        if not re.match(r'^[a-zA-Z0-9_\-]+$', task_id):
            return jsonify({"status": "error", "error": "Invalid task ID format"}), 400
            
        # Define paths to check for task files
        task_dir = os.path.join(RESULTS_DIR, task_id)
        records_dir = os.path.join(RESULTS_DIR, 'records', task_id)
        
        deleted = False
        
        # Check and delete from main results directory
        if os.path.isdir(task_dir):
            shutil.rmtree(task_dir)
            deleted = True
            
        # Check and delete from records subdirectory
        if os.path.isdir(records_dir):
            shutil.rmtree(records_dir)
            deleted = True
            
        # If nothing was found to delete
        if not deleted:
            return jsonify({"status": "error", "error": "Task not found"}), 404
            
        # Remove from task storage if it exists
        if task_id in task_storage:
            del task_storage[task_id]
            
        return jsonify({
            "status": "ok",
            "message": f"Task {task_id} deleted successfully"
        })
    except Exception as e:
        app.logger.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "error": f"Failed to delete task: {str(e)}"
        }), 500

@app.route('/api/history', methods=['GET'])
def api_get_history():
    """Get a list of previously generated tasks with their basic info"""
    # Make sure task_storage is up to date
    reload_task_storage()
    
    history_tasks = []
    
    # List all directories in the results folder
    for task_id in os.listdir(RESULTS_DIR):
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if not os.path.isdir(task_dir):
            continue
            
        # Check if this is a completed task with results
        result_file = os.path.join(task_dir, 'result.jsonl')
        if not os.path.exists(result_file):
            continue
            
        # Get the input file to extract the prompt
        input_file = os.path.join(task_dir, 'input.jsonl')
        prompt = ""
        task_type = "unknown"
        
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r') as f:
                    input_data = json.load(f)
                    if 'value' in input_data:
                        # Story generation input
                        prompt = input_data.get('value', '')
                        task_type = "story"
                    elif 'prompt' in input_data:
                        # Report generation input
                        prompt = input_data.get('prompt', '')
                        task_type = "report"
            except:
                # If we can't read the input file, continue anyway
                pass
        
        # Get the creation time of the result file as timestamp
        creation_time = os.path.getctime(result_file)
        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # Add task info to history list
        history_tasks.append({
            "taskId": task_id,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "type": task_type,
            "createdAt": creation_date
        })
    
    # Sort by creation time, newest first
    history_tasks.sort(key=lambda x: x["createdAt"], reverse=True)
    
    return jsonify({
        "history": history_tasks
    })

@app.route('/api/workspace/<task_id>', methods=['GET'])
def api_get_workspace(task_id):
    """Get the article.txt content for a task"""
    task_dir = os.path.join(RESULTS_DIR, 'records', task_id)
    article_file = os.path.join(task_dir, 'article.txt')
    
    if not os.path.exists(article_file):
        return jsonify({"error": "Workspace file not found"}), 404
    
    try:
        with open(article_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            "taskId": task_id,
            "workspace": content
        })
    except Exception as e:
        print(f"Error reading workspace file: {str(e)}")
        return jsonify({"error": f"Failed to read workspace file: {str(e)}"}), 500

@app.route('/api/ping', methods=['GET'])
def api_ping():
    """Simple endpoint to test if the API is reachable"""
    return jsonify({
        "status": "ok",
        "message": "API server is running",
        "version": "1.0.0"
    })

def monitor_task_progress(task_id, nodes_dir):
    """
    Monitor task progress and send updates via WebSocket
    """
    try:
        print(f"Starting task progress monitoring for task: {task_id}")
        print(f"Monitoring directory: {nodes_dir}")
        
        # Create a basic task structure to start with
        task_graph = {
            "id": "0",
            "goal": "Initializing task...",
            "task_type": "think",
            "status": "DOING",
            "sub_tasks": []
        }
        
        print(f"Sending initial task_update for {task_id}")
        socketio.emit('task_update', {'taskId': task_id, 'taskGraph': task_graph})
        
        # Monitor the nodes.json file for changes
        last_modified = 0
        nodes_file = os.path.join(nodes_dir, 'nodes.json')
        task_dir = os.path.dirname(nodes_dir)
        print(f"Watching for changes to: {nodes_file}")
        
        while task_storage.get(task_id, {}).get('status') not in ['completed', 'error', 'stopped']:                
            if os.path.exists(nodes_file):
                current_modified = os.path.getmtime(nodes_file)
                
                if current_modified > last_modified:
                    last_modified = current_modified
                    print(f"Detected changes to nodes.json, reading file")
                    
                    try:
                        with open(nodes_file, 'r') as f:
                            nodes_data = json.load(f)
                        
                        # Transform the data for frontend
                        transformed_graph = transform_node_to_graph(nodes_data, root=True)
                        
                        # Send update via WebSocket
                        print(f"Sending task_update with {len(transformed_graph.get('sub_tasks', []))} sub-tasks")
                        
                        # Debug output - check if we have action information
                        if 'latest_action' in transformed_graph:
                            print(f"Root node has latest action: {transformed_graph['latest_action']['name']}")
                        
                        # Debug the first subtask if available
                        if transformed_graph.get('sub_tasks') and len(transformed_graph.get('sub_tasks', [])) > 0:
                            first_task = transformed_graph['sub_tasks'][0]
                            if 'latest_action' in first_task:
                                print(f"First subtask has latest action: {first_task['latest_action']['name']}")
                        
                        socketio.emit('task_update', {
                            'taskId': task_id, 
                            'taskGraph': transformed_graph
                        })
                    except Exception as e:
                        print(f"Error reading nodes.json: {str(e)}")
            else:
                print(f"Waiting for nodes.json file to be created at: {nodes_file}")
            
            # Sleep for a short time to avoid high CPU usage
            time.sleep(1)
            
        print(f"Task {task_id} status changed to {task_storage.get(task_id, {}).get('status')}")
        # Send one final update once the task is complete
        if os.path.exists(nodes_file):
            try:
                print(f"Reading final state from nodes.json")
                with open(nodes_file, 'r') as f:
                    nodes_data = json.load(f)
                    
                transformed_graph = transform_node_to_graph(nodes_data, root=True)
                print(f"Sending final task_update with status {task_storage.get(task_id, {}).get('status')}")
                socketio.emit('task_update', {
                    'taskId': task_id, 
                    'taskGraph': transformed_graph,
                    'status': task_storage.get(task_id, {}).get('status', 'unknown')
                })
            except Exception as e:
                print(f"Error reading final nodes.json: {str(e)}")
        else:
            print(f"Warning: nodes.json file not found for final update: {nodes_file}")
    
    except Exception as e:
        print(f"Error in monitor_task_progress: {str(e)}")
        import traceback
        print(traceback.format_exc())

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send a test message to verify the connection works
    socketio.emit('connection_test', {'message': 'Connected successfully to the server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_to_task')
def handle_subscribe(data):
    print(f"Received subscription request: {data}")
    task_id = data.get('taskId')
    
    if not task_id:
        print("No taskId provided in subscription request")
        emit('subscription_status', {'status': 'error', 'message': 'No taskId provided', 'taskId': None})
        return
        
    print(f"Checking if task {task_id} exists in storage")
    # Always allow subscription, even if task doesn't exist yet (it might be starting)
    task_dir = os.path.join(RESULTS_DIR, task_id)
    nodes_dir = os.path.join(task_dir, 'records')
    
    if not os.path.exists(nodes_dir):
        print(f"Creating nodes directory: {nodes_dir}")
        os.makedirs(nodes_dir, exist_ok=True)
    
    # Start monitoring in a background thread
    print(f"Starting monitoring thread for task {task_id}")
    thread = threading.Thread(
        target=monitor_task_progress,
        args=(task_id, nodes_dir)
    )
    thread.daemon = True
    thread.start()
    
    print(f"Sending subscription confirmation for {task_id}")
    emit('subscription_status', {'status': 'subscribed', 'taskId': task_id})
    
    # Also send an initial update to confirm the subscription worked
    initial_graph = {
        "id": "0",
        "goal": "Task is initializing...",
        "task_type": "think",
        "status": "READY",
        "sub_tasks": []
    }
    emit('task_update', {'taskId': task_id, 'taskGraph': initial_graph})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=args.port, allow_unsafe_werkzeug=True)