#!/usr/bin/env python3

import os
import configparser
import stat
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


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
    config["behavior"]["remove_quotes"] = True
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


def validate_token(token: str) -> Tuple[bool, str]:
    """Validate the OpenRouter API token format.
    
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    # Basic validation - OpenRouter tokens typically start with "sk-or-"
    if not token.startswith("sk-or-"):
        return False, "Token doesn't match expected OpenRouter format (should start with 'sk-or-')"
    
    # Check minimum length
    if len(token) < 20:
        return False, "Token is too short to be valid"
        
    return True, "Token format is valid"


def mask_token(token: str) -> str:
    """Mask the token for display purposes."""
    if not token or len(token) <= 10:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


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


def save_config_secure(config: Dict[str, Any], path: Optional[Path] = None) -> None:
    """Save configuration with secure file permissions."""
    # Save the config
    save_config(config, path)
    
    if path is None:
        path = get_config_path()
    
    # Set secure permissions (readable/writable only by the owner)
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    except Exception as e:
        print(f"Warning: Could not set secure permissions on config file: {e}")


def set_token(token: str) -> Tuple[bool, str]:
    """Set the OpenRouter API token in the configuration.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Validate the token
    is_valid, message = validate_token(token)
    if not is_valid:
        return False, f"Invalid token: {message}"
    
    # Load existing config
    config = load_config()
    
    # Update the token
    config["provider"]["api_key"] = token
    
    # Save with secure permissions
    try:
        save_config_secure(config)
        return True, f"Token {mask_token(token)} saved successfully"
    except Exception as e:
        return False, f"Failed to save token: {e}"


def get_token() -> Tuple[Optional[str], str]:
    """Get the OpenRouter API token from the configuration.
    
    Returns:
        Tuple[Optional[str], str]: (token, message)
    """
    config = load_config()
    token = config.get("provider", {}).get("api_key")
    
    if not token:
        return None, "No API token configured. Use 'unfck config set-token' to set one."
    
    return token, f"Current token: {mask_token(token)}"


def set_config_value(section: str, key: str, value: str) -> Tuple[bool, str]:
    """Set a configuration value.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Load existing config
    config = load_config()
    
    # Ensure section exists
    if section not in config:
        return False, f"Invalid section: {section}"
    
    # Convert value to appropriate type
    if value.lower() in ("true", "yes", "1"):
        typed_value = True
    elif value.lower() in ("false", "no", "0"):
        typed_value = False
    elif value.isdigit():
        typed_value = int(value)
    else:
        typed_value = value
    
    # Update the value
    config[section][key] = typed_value
    
    # Save the config
    try:
        save_config(config)
        return True, f"Set {section}.{key} = {value}"
    except Exception as e:
        return False, f"Failed to save configuration: {e}"


def get_config_value(section: str, key: str) -> Tuple[Optional[Any], str]:
    """Get a configuration value.
    
    Returns:
        Tuple[Optional[Any], str]: (value, message)
    """
    config = load_config()
    
    if section not in config:
        return None, f"Invalid section: {section}"
    
    if key not in config[section]:
        return None, f"Key '{key}' not found in section '{section}'"
    
    value = config[section][key]
    return value, f"{section}.{key} = {value}"


def list_config() -> Dict[str, Dict[str, Any]]:
    """List all configuration values.
    
    Returns:
        Dict[str, Dict[str, Any]]: The configuration dictionary
    """
    config = load_config()
    
    # Mask the API key if present
    if "provider" in config and "api_key" in config["provider"] and config["provider"]["api_key"]:
        config["provider"]["api_key"] = mask_token(config["provider"]["api_key"])
    
    return config
