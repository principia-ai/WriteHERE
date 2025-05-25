import os
import threading
from flask_socketio import emit

from .task_manager import monitor_task_progress, RESULTS_DIR, socketio


def register_handlers(sio):
    """Attach Socket.IO event handlers to the given SocketIO instance."""

    @sio.on('connect')
    def handle_connect():
        print('Client connected')
        sio.emit('connection_test', {'message': 'Connected successfully to the server'})

    @sio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @sio.on('subscribe_to_task')
    def handle_subscribe(data):
        print(f"Received subscription request: {data}")
        task_id = data.get('taskId')
        if not task_id:
            emit('subscription_status', {'status': 'error', 'message': 'No taskId provided', 'taskId': None})
            return

        task_dir = os.path.join(RESULTS_DIR, task_id)
        nodes_dir = os.path.join(task_dir, 'records')
        if not os.path.exists(nodes_dir):
            os.makedirs(nodes_dir, exist_ok=True)

        thread = threading.Thread(target=monitor_task_progress, args=(task_id, nodes_dir))
        thread.daemon = True
        thread.start()

        emit('subscription_status', {'status': 'subscribed', 'taskId': task_id})
        initial_graph = {"id": "0", "goal": "Task is initializing...", "task_type": "think", "status": "READY", "sub_tasks": []}
        emit('task_update', {'taskId': task_id, 'taskGraph': initial_graph})

