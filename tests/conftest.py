"""Makes the project's top-level modules importable when running
pytest from the project root (e.g. `pytest` or `pytest tests/`).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
