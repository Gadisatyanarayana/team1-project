"""Vercel serverless entrypoint exposing the Flask app."""

import os
import sys

# Resolve project root from this file's location (api/index.py → project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Set the working directory so CSV file lookups work
os.chdir(PROJECT_ROOT)

from src.ui.app import create_app

app = create_app()
