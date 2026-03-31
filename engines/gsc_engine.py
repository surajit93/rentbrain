import json


def load_gsc():
    try:
        with open("logs/gsc_export.json") as f:
            return json.load(f)
    except Exception:
        return []
