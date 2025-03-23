#!/usr/bin/env python3

import os
import configparser
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    # Check for config in the current directory first
    local_config = Path(".unfckrc")
    if local_config.exists():
        return local_config

    # Then check in the user's home directory
    home_config = Path.home() / ".unfckrc"
    return home_config


def load_config() -> Dict[str, Any]:
    """Load configuration from file and environment variables."""
    config: Dict[str, Dict[str, Any]] = {
        "provider": {},
        "defaults": {},
        "behavior": {},
        "formatting": {}
    }

    # Default values
    config["defaults"]["default_commit_count"] = 5
    config["defaults"]["auto_apply"] = False
    config["defaults"]["prompt_user_for_why"] = True
    config["behavior"]["show_diff"] = True
    config["behavior"]["skip_merge_commits"] = True
    config["behavior"]["warn_on_shared_branches"] = True
    config["formatting"]["use_color"] = True
    config["formatting"]["message_style"] = "descriptive"
    config["provider"]["engine"] = "gpt-4"

    # Load from config file if it exists
    config_path = get_config_path()
    if config_path.exists():
        parser = configparser.ConfigParser()
        parser.read(config_path)
        
        # Convert ConfigParser object to our dictionary structure
        for section in parser.sections():
            if section not in config:
                config[section] = {}
            
            for key, value in parser.items(section):
                # Convert string values to appropriate types
                if value.lower() in ("true", "yes", "1"):
                    config[section][key] = True
                elif value.lower() in ("false", "no", "0"):
                    config[section][key] = False
                elif value.isdigit():
                    config[section][key] = int(value)
                else:
                    config[section][key] = value

    # Override with environment variables
    if "OPENROUTER_API_KEY" in os.environ:
        config["provider"]["api_key"] = os.environ["OPENROUTER_API_KEY"]
    
    if "UNFCK_MODEL" in os.environ:
        config["provider"]["engine"] = os.environ["UNFCK_MODEL"]
    
    if "UNFCK_AUTO_APPLY" in os.environ:
        config["defaults"]["auto_apply"] = os.environ["UNFCK_AUTO_APPLY"].lower() in ("true", "yes", "1")
    
    return config


def save_config(config: Dict[str, Any], path: Optional[Path] = None) -> None:
    """Save configuration to file."""
    if path is None:
        path = get_config_path()
    
    parser = configparser.ConfigParser()
    
    # Convert our dictionary to ConfigParser format
    for section, values in config.items():
        parser[section] = {}
        for key, value in values.items():
            parser[section][key] = str(value)
    
    # Write to file
    with open(path, "w") as f:
        parser.write(f)
