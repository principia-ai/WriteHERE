import os
import json
import subprocess
import threading
import time
from datetime import datetime

# Global storage for tasks
task_storage = {}

# Directory to store task results
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# SocketIO instance will be set by server.py
socketio = None

def set_socketio(sio):
    """Store the SocketIO instance for later use."""
    global socketio
    socketio = sio


def reload_task_storage():
    """Reload task metadata from disk into memory."""
    global task_storage

    for task_id in os.listdir(RESULTS_DIR):
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if not os.path.isdir(task_dir):
            continue

        result_file = os.path.join(task_dir, 'result.jsonl')
        done_file = os.path.join(task_dir, 'done.txt')
        if os.path.exists(result_file):
            if task_id not in task_storage:
                creation_time = os.path.getctime(task_dir)
                task_storage[task_id] = {
                    "status": "completed" if os.path.exists(done_file) else "running",
                    "start_time": creation_time,
                }

                run_sh_file = os.path.join(task_dir, 'run.sh')
                if os.path.exists(run_sh_file):
                    try:
                        with open(run_sh_file, 'r') as f:
                            run_script = f.read()
                            if "--model " in run_script:
                                model = run_script.split("--model ")[1].split(" ")[0]
                                task_storage[task_id]["model"] = model
                            if "--engine-backend " in run_script:
                                engine_backend = run_script.split("--engine-backend ")[1].split(" ")[0]
                                if engine_backend != "none":
                                    task_storage[task_id]["search_engine"] = engine_backend
                    except Exception as e:  # pragma: no cover - debug output
                        print(f"Error extracting model info from run.sh for {task_id}: {e}")

                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        task_storage[task_id]["result"] = result_data.get("result", "No result available")
                except Exception as e:  # pragma: no cover - debug output
                    print(f"Error loading result file for {task_id}: {e}")
                    task_storage[task_id]["error"] = f"Failed to load output file: {e}"


# Helper used by monitor_task_progress and /api/task-graph

def transform_node_to_graph(node, seen_nodes=None, root=False):
    """Convert internal node representation to frontend friendly graph."""
    if seen_nodes is None:
        seen_nodes = set()

    task_info = node.get("task_info", {})
    node_id = node.get("nid", "")

    if node_id in seen_nodes and not root:
        return None
    seen_nodes.add(node_id)

    is_execute_node = node.get("node_type") == "EXECUTE_NODE"
    transformed = {
        "id": node_id,
        "goal": task_info.get("goal", "Unknown"),
        "task_type": task_info.get("task_type", "unknown"),
        "status": node.get("status", "UNKNOWN"),
        "dependency": task_info.get("dependency", []),
        "sub_tasks": [],
        "node_type": node.get("node_type", "UNKNOWN"),
        "is_execute_node": is_execute_node,
    }

    if "result" in node:
        actions = []
        latest_action_name = None
        latest_action_result = None
        for action_name, action_data in node.get("result", {}).items():
            raw_result = action_data.get("result", {})
            action_result = raw_result.get("result", "") if isinstance(raw_result, dict) else raw_result
            action_time = action_data.get("time", "")
            actions.append({"name": action_name, "result": action_result, "time": action_time})
            if not latest_action_name or action_time > node.get("result", {}).get(latest_action_name, {}).get("time", ""):
                latest_action_name = action_name
                latest_action_result = action_result
        if actions:
            transformed["actions"] = actions
        if latest_action_name:
            transformed["latest_action"] = {"name": latest_action_name, "result": latest_action_result}

    def collect_subtasks(current_node, parent_transformed):
        inner = current_node.get("inner_graph", {})
        if not inner or "topological_task_queue" not in inner:
            return
        tasks = inner.get("topological_task_queue", [])
        sorted_tasks = sorted(tasks, key=lambda x: int(str(x.get("nid", "0")).split(".")[-1]))
        for task in sorted_tasks:
            task_id = task.get("nid", "")
            if task_id in seen_nodes and task_id != current_node.get("nid"):
                continue
            seen_nodes.add(task_id)
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
                "is_execute_node": is_execute,
            }
            if "result" in task:
                actions = []
                latest_action_name = None
                latest_action_result = None
                for action_name, action_data in task.get("result", {}).items():
                    raw_result = action_data.get("result", {})
                    action_result = raw_result.get("result", "") if isinstance(raw_result, dict) else raw_result
                    action_time = action_data.get("time", "")
                    actions.append({"name": action_name, "result": action_result, "time": action_time})
                    if not latest_action_name or action_time > task.get("result", {}).get(latest_action_name, {}).get("time", ""):
                        latest_action_name = action_name
                        latest_action_result = action_result
                if actions:
                    sub_task["actions"] = actions
                if latest_action_name:
                    sub_task["latest_action"] = {"name": latest_action_name, "result": latest_action_result}
            parent_transformed["sub_tasks"].append(sub_task)
            collect_subtasks(task, sub_task)

    collect_subtasks(node, transformed)
    return transformed


def run_story_generation(task_id, prompt, model, api_keys):
    """Run the story generation engine as a subprocess."""
    task_dir = os.path.join(RESULTS_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    records_dir = os.path.join(task_dir, 'records')
    os.makedirs(records_dir, exist_ok=True)

    input_file = os.path.join(task_dir, 'input.jsonl')
    with open(input_file, 'w') as f:
        json.dump({"id": task_id, "field": "inputs", "value": prompt, "ori": {"example_id": task_id, "inputs": prompt, "subset": "user"}}, f)
        f.write('\n')

    output_file = os.path.join(task_dir, 'result.jsonl')
    done_file = os.path.join(task_dir, 'done.txt')
    nodes_file = os.path.join(records_dir, 'nodes.json')

    env = os.environ.copy()
    if api_keys.get('openai'):
        env['OPENAI'] = api_keys['openai']
    if api_keys.get('claude'):
        env['CLAUDE'] = api_keys['claude']
    if api_keys.get('gemini'):
        env['GEMINI'] = api_keys['gemini']
    if api_keys.get('serpapi'):
        env['SERPAPI'] = api_keys['serpapi']

    script_path = os.path.join(task_dir, 'run.sh')
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
cd {os.path.abspath(os.path.join(os.path.dirname(__file__), '../recursive'))}
python engine.py --filename {input_file} --output-filename {output_file} --done-flag-file {done_file} --model {model} --mode story --nodes-json-file {nodes_file}
""")
    os.chmod(script_path, 0o755)

    task_storage[task_id] = {"status": "running", "start_time": time.time(), "model": model}

    monitoring_thread = threading.Thread(target=monitor_task_progress, args=(task_id, records_dir))
    monitoring_thread.daemon = True
    monitoring_thread.start()

    try:
        process = subprocess.Popen(['/bin/bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        task_storage[task_id]["process"] = process
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            task_storage[task_id]["status"] = "completed"
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
    except Exception as e:  # pragma: no cover - subprocess errors
        task_storage[task_id]["status"] = "error"
        task_storage[task_id]["error"] = str(e)


def run_report_generation(task_id, prompt, model, enable_search, search_engine, api_keys):
    """Run the report generation engine as a subprocess."""
    task_dir = os.path.join(RESULTS_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    records_dir = os.path.join(task_dir, 'records')
    os.makedirs(records_dir, exist_ok=True)

    input_file = os.path.join(task_dir, 'input.jsonl')
    with open(input_file, 'w') as f:
        json.dump({"topic": "", "intent": "", "domain": "", "id": task_id, "prompt": prompt}, f)
        f.write('\n')

    output_file = os.path.join(task_dir, 'result.jsonl')
    done_file = os.path.join(task_dir, 'done.txt')
    nodes_file = os.path.join(records_dir, 'nodes.json')

    env = os.environ.copy()
    if api_keys.get('openai'):
        env['OPENAI'] = api_keys['openai']
    if api_keys.get('claude'):
        env['CLAUDE'] = api_keys['claude']
    if api_keys.get('gemini'):
        env['GEMINI'] = api_keys['gemini']
    if api_keys.get('serpapi'):
        env['SERPAPI'] = api_keys['serpapi']

    script_path = os.path.join(task_dir, 'run.sh')
    engine_backend = search_engine if enable_search else "none"
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
cd {os.path.abspath(os.path.join(os.path.dirname(__file__), '../recursive'))}
python engine.py --filename {input_file} --output-filename {output_file} --done-flag-file {done_file} --model {model} --engine-backend {engine_backend} --mode report --nodes-json-file {nodes_file}
""")
    os.chmod(script_path, 0o755)

    task_storage[task_id] = {
        "status": "running",
        "start_time": time.time(),
        "model": model,
        "search_engine": engine_backend if enable_search else None,
    }

    monitoring_thread = threading.Thread(target=monitor_task_progress, args=(task_id, records_dir))
    monitoring_thread.daemon = True
    monitoring_thread.start()

    try:
        process = subprocess.Popen(['/bin/bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        task_storage[task_id]["process"] = process
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            task_storage[task_id]["status"] = "completed"
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
    except Exception as e:  # pragma: no cover
        task_storage[task_id]["status"] = "error"
        task_storage[task_id]["error"] = str(e)


def monitor_task_progress(task_id, nodes_dir):
    """Watch a task's nodes.json and emit updates via WebSocket."""
    if socketio is None:
        return
    try:
        task_graph = {"id": "0", "goal": "Initializing task...", "task_type": "think", "status": "DOING", "sub_tasks": []}
        socketio.emit('task_update', {'taskId': task_id, 'taskGraph': task_graph})
        last_modified = 0
        nodes_file = os.path.join(nodes_dir, 'nodes.json')
        while task_storage.get(task_id, {}).get('status') not in ['completed', 'error', 'stopped']:
            if os.path.exists(nodes_file):
                current_modified = os.path.getmtime(nodes_file)
                if current_modified > last_modified:
                    last_modified = current_modified
                    try:
                        with open(nodes_file, 'r') as f:
                            nodes_data = json.load(f)
                        transformed_graph = transform_node_to_graph(nodes_data, root=True)
                        socketio.emit('task_update', {'taskId': task_id, 'taskGraph': transformed_graph})
                    except Exception as e:  # pragma: no cover - debug
                        print(f"Error reading nodes.json: {e}")
            time.sleep(1)
        if os.path.exists(nodes_file):
            try:
                with open(nodes_file, 'r') as f:
                    nodes_data = json.load(f)
                transformed_graph = transform_node_to_graph(nodes_data, root=True)
                socketio.emit('task_update', {
                    'taskId': task_id,
                    'taskGraph': transformed_graph,
                    'status': task_storage.get(task_id, {}).get('status', 'unknown'),
                })
            except Exception as e:  # pragma: no cover
                print(f"Error reading final nodes.json: {e}")
    except Exception as e:  # pragma: no cover
        print(f"Error in monitor_task_progress: {e}")

