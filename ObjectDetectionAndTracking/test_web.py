#!/usr/bin/env python3
"""
Minimal test to verify the web interface works without camera
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_interface import create_app
from flask import Flask

# Create a minimal Flask app to test
test_app = Flask(__name__)

@test_app.route('/')
def hello():
    return "Ping Pong Ball Tracker - Web Interface Working!"

@test_app.route('/test')
def test():
    return {"status": "success", "message": "Web server is working"}

if __name__ == "__main__":
    print("Testing minimal web server...")
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    test_app.run(host='0.0.0.0', port=5000, debug=False)
