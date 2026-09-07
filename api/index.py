from fastapi import FastAPI
import sys, os
# Ensure the project root is in PYTHONPATH so imports work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from server import app  # noqa: F401  (FastAPI app instance)
