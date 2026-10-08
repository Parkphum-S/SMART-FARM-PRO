import json


def parse_payload(payload: bytes) -> dict | None:
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

    return data if isinstance(data, dict) else None
