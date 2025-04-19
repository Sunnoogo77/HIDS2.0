# utils/json_handler.py
import json
import os
from typing import Any

def read_json(filepath: str) -> Any:
    """Read and return JSON content from a file."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def write_json(filepath: str, data: Any) -> None:
    """Write data to a JSON file, pretty formatted."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def init_json_if_missing(filepath: str, default_data: Any) -> None:
    """Create the file with default content if it doesn't exist."""
    if not os.path.exists(filepath):
        write_json(filepath, default_data)