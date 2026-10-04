"""Launch the placement dashboard from the workspace root (D:\\DWM)."""
from pathlib import Path
import runpy

project_app = Path(__file__).resolve().parents[1] / "placement-dwm-project" / "web" / "app.py"
if not project_app.is_file():
    raise SystemExit(f"Placement dashboard not found: {project_app}")

runpy.run_path(str(project_app), run_name="__main__")
