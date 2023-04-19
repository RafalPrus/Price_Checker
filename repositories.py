import json
import os


DATA_FILE = "data/tracked_links.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        data = {key: value for key, value in sorted(data.items())}
        json.dump(data, f)