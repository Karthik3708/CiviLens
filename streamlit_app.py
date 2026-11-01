"""
CiviLens — Root Entrypoint for Streamlit Cloud Deployment
Routes seamlessly to backend/streamlit_app.py
"""

import sys
import runpy
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Execute the main Streamlit application
backend_app = backend_dir / "streamlit_app.py"
runpy.run_path(str(backend_app), run_name="__main__")

