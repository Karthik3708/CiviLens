"""
CiviLens Main Entrypoint
Routes execution to streamlit_app.py
"""
import sys
import runpy
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

app_path = backend_dir / "streamlit_app.py"
runpy.run_path(str(app_path), run_name="__main__")
