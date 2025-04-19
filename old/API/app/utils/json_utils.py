import json

def read_json(file_path):
    """
    Read a JSON file and return the data as a dictionary.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    except json.JSONDecodeError:
        return {}

def write_json(file_path, data):
    """
    Write data to a JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    