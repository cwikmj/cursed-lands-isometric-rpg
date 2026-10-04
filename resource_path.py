from pathlib import Path
import sys

def resource_path(relative_path):
    """Return the path to a bundled resource."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path
