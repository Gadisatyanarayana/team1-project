"""Vercel serverless entrypoint for the Flask app.

Vercel runs this file as a Python WSGI handler. The `app` object must be
exported at module level for Vercel's Python runtime to pick it up.
Do NOT use os.chdir() — it's unreliable in serverless; always use
absolute paths derived from __file__.
"""

import os
import sys

# ── Resolve absolute project root (api/index.py → project root) ────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Inject PROJECT_ROOT so engine.py and dictionary.py can resolve the CSV
# path reliably without relying on cwd (unreliable in serverless)
os.environ.setdefault('TRANSLATOR_ROOT', PROJECT_ROOT)

from src.ui.app import create_app

app = create_app()
