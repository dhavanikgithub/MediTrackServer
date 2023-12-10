import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application instance from app.py
from app import app

# Define the application variable for Gunicorn
application = app

# If you need to set up any additional configurations for Gunicorn, you can add them here
