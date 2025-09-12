from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import argparse

from . import task_manager
from .routes import routes_bp
from .socketio_handlers import register_handlers

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

task_manager.set_socketio(socketio)

app.register_blueprint(routes_bp)
register_handlers(socketio)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backend server for WriteHERE application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    args = parser.parse_args()
    socketio.run(app, debug=True, host="0.0.0.0", port=args.port, allow_unsafe_werkzeug=True)
