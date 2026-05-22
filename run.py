# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

# Force UTF-8 encoding for Python environment on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables from .env file BEFORE importing app
load_dotenv()

# Import app factory and socketio from the app package
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Define host and port
    host = '127.0.0.1'
    port = 5000

    # Print the URL clearly in the console
    print(f"\n{'='*50}")
    print(f"Pawfect Finds Web App Starting...")
    print(f"{'='*50}")
    print(f"URL: http://{host}:{port}")
    print(f"SocketIO: Enabled")
    print(f"{'='*50}\n")

    # Run the app with SocketIO (async_mode threading avoids httpx proxy conflicts)
    socketio.run(app, debug=True, host=host, port=port, allow_unsafe_werkzeug=True)
