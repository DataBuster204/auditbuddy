# config_loader.py
# This file reads the config.yaml and makes the settings available
# throughout the app. Think of it as the app's control panel.

import yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)