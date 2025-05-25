from flask import Blueprint, request, jsonify
import os
import json
import uuid
import threading
import subprocess
import shutil
import re
from datetime import datetime

from . import task_manager
from .task_manager import (
    run_story_generation,
    run_report_generation,
    reload_task_storage,
    task_storage,
    RESULTS_DIR,
    transform_node_to_graph,
    socketio,
)

routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/api/generate-story', methods=['POST'])
def api_generate_story():
    data = request.json
    for field in ['prompt', 'model', 'apiKeys']:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    task_id = f"story-{uuid.uuid4()}"
    thread = threading.Thread(target=run_story_generation, args=(task_id, data['prompt'], data['model'], data['apiKeys']))
    thread.start()

    return jsonify({"taskId": task_id, "status": "started"})


@routes_bp.route('/api/generate-report', methods=['POST'])
def api_generate_report():
    data = request.json
    for field in ['prompt', 'model', 'apiKeys']:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    enable_search = data.get('enableSearch', True)
    search_engine = data.get('searchEngine', 'google')

    task_id = f"report-{uuid.uuid4()}"
    thread = threading.Thread(target=run_report_generation,
                              args=(task_id, data['prompt'], data['model'], enable_search, search_engine, data['apiKeys']))
    thread.start()

    return jsonify({"taskId": task_id, "status": "started"})


@routes_bp.route('/api/status/<task_id>', methods=['GET'])
def api_get_status(task_id):
    if task_id not in task_storage:
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if os.path.isdir(task_dir):
            result_file = os.path.join(task_dir, 'result.jsonl')
            done_file = os.path.join(task_dir, 'done.txt')
            if os.path.exists(result_file):
                creation_time = os.path.getctime(task_dir)
                task_storage[task_id] = {
                    "status": "completed" if os.path.exists(done_file) else "running",
                    "start_time": creation_time,
                }
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        task_storage[task_id]["result"] = result_data.get("result", "No result available")
                except Exception as e:
                    task_storage[task_id]["error"] = f"Failed to load output file: {e}"
            else:
                return jsonify({"error": "Task not found or incomplete"}), 404
        else:
            return jsonify({"error": "Task not found"}), 404

    task = task_storage[task_id]
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
        "searchEngine": task.get("search_engine"),
    })


@routes_bp.route('/api/result/<task_id>', methods=['GET'])
def api_get_result(task_id):
    if task_id not in task_storage:
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if os.path.isdir(task_dir):
            result_file = os.path.join(task_dir, 'result.jsonl')
            done_file = os.path.join(task_dir, 'done.txt')
            if os.path.exists(result_file):
                creation_time = os.path.getctime(task_dir)
                task_storage[task_id] = {
                    "status": "completed" if os.path.exists(done_file) else "running",
                    "start_time": creation_time,
                }
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        task_storage[task_id]["result"] = result_data.get("result", "No result available")
                except Exception as e:
                    task_storage[task_id]["error"] = f"Failed to load output file: {e}"
                    return jsonify({"error": f"Failed to load output file: {e}"}), 500
            else:
                return jsonify({"error": "Task result file not found"}), 404
        else:
            return jsonify({"error": "Task not found"}), 404

    result_md_dir = os.path.join(RESULTS_DIR, 'records', task_id, 'report.md')
    task = task_storage[task_id]
    if "result" not in task:
        if not os.path.exists(result_md_dir):
            return jsonify({"error": "Task result not available"}), 400
        else:
            with open(result_md_dir, 'r') as f:
                task["result"] = f.read()

    return jsonify({"taskId": task_id, "result": task.get("result", "No result available"), "model": task.get("model", "unknown"), "searchEngine": task.get("search_engine")})


@routes_bp.route('/api/task-graph/<task_id>', methods=['GET'])
def api_get_task_graph(task_id):
    task_dir = os.path.join(RESULTS_DIR, task_id)
    if not os.path.isdir(task_dir):
        return jsonify({"error": "Task not found"}), 404

    nodes_paths = [
        os.path.join(task_dir, 'records', 'nodes.json'),
        os.path.join(RESULTS_DIR, 'records', task_id, 'nodes.json'),
    ]

    nodes_file = None
    for path in nodes_paths:
        if os.path.exists(path):
            nodes_file = path
            break

    if not nodes_file:
        input_file = os.path.join(task_dir, 'input.jsonl')
        prompt = "Unknown task"
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r') as f:
                    input_data = json.load(f)
                    if 'value' in input_data:
                        prompt = input_data.get('value', '')
            except Exception:
                pass
        simple_graph = {
            "id": "",
            "goal": prompt,
            "task_type": "write",
            "status": "FINISH",
            "sub_tasks": [{"id": "0", "goal": "Task graph data not available", "task_type": "think", "status": "FINISH", "sub_tasks": []}],
        }
        return jsonify({"taskId": task_id, "taskGraph": simple_graph})

    try:
        with open(nodes_file, 'r') as f:
            nodes_data = json.load(f)
        transformed_graph = transform_node_to_graph(nodes_data, root=True)
        return jsonify({"taskId": task_id, "taskGraph": transformed_graph})
    except Exception as e:
        return jsonify({"error": f"Failed to read task graph data: {e}"}), 500


@routes_bp.route('/api/reload', methods=['POST'])
def api_reload_tasks():
    reload_task_storage()
    return jsonify({"status": "ok", "message": "Task storage reloaded", "taskCount": len(task_storage)})


@routes_bp.route('/api/stop-task/<task_id>', methods=['POST'])
def api_stop_task(task_id):
    try:
        if not re.match(r'^[a-zA-Z0-9_\-]+$', task_id):
            return jsonify({"status": "error", "error": "Invalid task ID format"}), 400
        if task_id not in task_storage:
            return jsonify({"status": "error", "error": "Task not found"}), 404
        if task_storage[task_id]["status"] in ["completed", "error", "stopped"]:
            return jsonify({"status": "ok", "message": f"Task {task_id} is already {task_storage[task_id]['status']}"})

        task_dir = os.path.join(RESULTS_DIR, task_id)
        stop_file = os.path.join(task_dir, 'stop.txt')

        try:
            cmd = f"ps -ef | grep '{task_id}' | grep 'engine.py' | grep -v grep | awk '{{print $2}}'"
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                pid = int(result)
                if os.name != 'nt':
                    os.system(f"kill -9 {pid}")
                    os.system(f"pkill -P {pid}")
                else:
                    os.system(f"taskkill /F /PID {pid} /T")
            else:
                cmd = f"ps -ef | grep '{task_dir}/run.sh' | grep -v grep | awk '{{print $2}}'"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    pid = int(result)
                    if os.name != 'nt':
                        os.system(f"kill -9 {pid}")
                    else:
                        os.system(f"taskkill /F /PID {pid} /T")
        except Exception as e:
            if os.name != 'nt':
                os.system(f"pkill -f '{task_dir}'")

        with open(os.path.join(task_dir, 'done.txt'), 'w') as f:
            f.write("Stopped by user at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        task_storage[task_id]["status"] = "stopped"
        task_storage[task_id]["result"] = "Task was stopped by user request before completion."
        if socketio:
            socketio.emit('task_update', {'taskId': task_id, 'status': 'stopped', 'message': 'Task has been stopped by user request'})
        return jsonify({"status": "ok", "message": f"Task {task_id} has been stopped"})
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to stop task: {e}"}), 500


@routes_bp.route('/api/delete-task/<task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    try:
        if not re.match(r'^[a-zA-Z0-9_\-]+$', task_id):
            return jsonify({"status": "error", "error": "Invalid task ID format"}), 400
        task_dir = os.path.join(RESULTS_DIR, task_id)
        records_dir = os.path.join(RESULTS_DIR, 'records', task_id)
        deleted = False
        if os.path.isdir(task_dir):
            shutil.rmtree(task_dir)
            deleted = True
        if os.path.isdir(records_dir):
            shutil.rmtree(records_dir)
            deleted = True
        if not deleted:
            return jsonify({"status": "error", "error": "Task not found"}), 404
        if task_id in task_storage:
            del task_storage[task_id]
        return jsonify({"status": "ok", "message": f"Task {task_id} deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to delete task: {e}"}), 500


@routes_bp.route('/api/history', methods=['GET'])
def api_get_history():
    reload_task_storage()
    history_tasks = []
    for task_id in os.listdir(RESULTS_DIR):
        task_dir = os.path.join(RESULTS_DIR, task_id)
        if not os.path.isdir(task_dir):
            continue
        result_file = os.path.join(task_dir, 'result.jsonl')
        if not os.path.exists(result_file):
            continue
        input_file = os.path.join(task_dir, 'input.jsonl')
        prompt = ""
        task_type = "unknown"
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r') as f:
                    input_data = json.load(f)
                    if 'value' in input_data:
                        prompt = input_data.get('value', '')
                        task_type = "story"
                    elif 'prompt' in input_data:
                        prompt = input_data.get('prompt', '')
                        task_type = "report"
            except Exception:
                pass
        creation_time = os.path.getctime(result_file)
        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
        history_tasks.append({"taskId": task_id, "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt, "type": task_type, "createdAt": creation_date})
    history_tasks.sort(key=lambda x: x["createdAt"], reverse=True)
    return jsonify({"history": history_tasks})


@routes_bp.route('/api/workspace/<task_id>', methods=['GET'])
def api_get_workspace(task_id):
    task_dir = os.path.join(RESULTS_DIR, 'records', task_id)
    article_file = os.path.join(task_dir, 'article.txt')
    if not os.path.exists(article_file):
        return jsonify({"error": "Workspace file not found"}), 404
    try:
        with open(article_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"taskId": task_id, "workspace": content})
    except Exception as e:
        return jsonify({"error": f"Failed to read workspace file: {e}"}), 500


@routes_bp.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify({"status": "ok", "message": "API server is running", "version": "1.0.0"})

