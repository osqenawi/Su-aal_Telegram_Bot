"""../utils/json_utils.py"""

import json


def load_json_file(file_path) -> dict:
    """Loads a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
