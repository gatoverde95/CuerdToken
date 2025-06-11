#!/usr/bin/env python3
import json
import os

CONFIG_FILE = os.path.expanduser('~/.config/cuerdtoken/config.json')

def ensure_config_dir():
    """Ensure configuration directory exists"""
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

def save_config(config):
    """Save configuration to file"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f)

def load_config():
    """Load configuration from file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"language": "en"}  # Default config