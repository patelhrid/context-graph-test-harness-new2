"""Application configuration loader."""

APP_PORT = 8080
DEBUG_MODE = False


def load_config(path: str = "config.json") -> dict:
    """Load config from a JSON file and apply overrides."""
    import json
    with open(path) as f:
        cfg = json.load(f)
    cfg.setdefault("port", APP_PORT)
    cfg.setdefault("debug", DEBUG_MODE)
    return cfg
