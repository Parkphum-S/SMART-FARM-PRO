import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Use a test-only secret for this pytest process.
# This does not modify the project's .env file.
os.environ["JWT_SECRET"] = "test-only-secret-for-pytest-32-bytes-long"
