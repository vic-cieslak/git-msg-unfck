#!/usr/bin/env python3

import os
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import load_config, save_config, get_config_path


class TestConfig(unittest.TestCase):
    """Test cases for the config module."""
    
    def test_get_config_path(self):
        """Test that get_config_path returns the correct path."""
        # Mock the existence of a local config file
        with patch.object(Path, 'exists', return_value=True):
            config_path = get_config_path()
            self.assertEqual(config_path, Path(".unfckrc"))
        
        # Mock the absence of a local config file
        with patch.object(Path, 'exists', return_value=False):
            config_path = get_config_path()
            self.assertEqual(config_path, Path.home() / ".unfckrc")
    
    def test_load_config_defaults(self):
        """Test that load_config returns default values when no config file exists."""
        # Mock the absence of a config file
        with patch.object(Path, 'exists', return_value=False):
            config = load_config()
            
            # Check default values
            self.assertEqual(config["defaults"]["default_commit_count"], 5)
            self.assertEqual(config["defaults"]["auto_apply"], False)
            self.assertEqual(config["defaults"]["prompt_user_for_why"], True)
            self.assertEqual(config["behavior"]["show_diff"], True)
            self.assertEqual(config["provider"]["engine"], "gpt-4")
    
    def test_load_config_from_file(self):
        """Test that load_config correctly loads values from a config file."""
        # Mock config file content
        mock_config_content = """
[provider]
api_key = test_api_key
engine = claude-3.5

[defaults]
auto_apply = true
default_commit_count = 10
"""
        
        # Mock the existence of a config file and its content
        with patch.object(Path, 'exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_config_content)):
            config = load_config()
            
            # Check loaded values
            self.assertEqual(config["provider"]["api_key"], "test_api_key")
            self.assertEqual(config["provider"]["engine"], "claude-3.5")
            self.assertEqual(config["defaults"]["auto_apply"], True)
            self.assertEqual(config["defaults"]["default_commit_count"], 10)
    
    def test_load_config_from_env(self):
        """Test that load_config correctly loads values from environment variables."""
        # Mock environment variables
        env_vars = {
            "OPENROUTER_API_KEY": "env_api_key",
            "UNFCK_MODEL": "gpt-4",
            "UNFCK_AUTO_APPLY": "true"
        }
        
        # Mock the absence of a config file and environment variables
        with patch.object(Path, 'exists', return_value=False), \
             patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            
            # Check loaded values from environment
            self.assertEqual(config["provider"]["api_key"], "env_api_key")
            self.assertEqual(config["provider"]["engine"], "gpt-4")
            self.assertEqual(config["defaults"]["auto_apply"], True)
    
    def test_save_config(self):
        """Test that save_config correctly saves the configuration to a file."""
        # Test config to save
        test_config = {
            "provider": {
                "api_key": "test_api_key",
                "engine": "claude-3.5"
            },
            "defaults": {
                "auto_apply": True,
                "default_commit_count": 10
            }
        }
        
        # Mock open for writing
        mock_file = mock_open()
        
        # Mock the config path
        with patch('builtins.open', mock_file), \
             patch('src.config.get_config_path', return_value=Path("/mock/path/.unfckrc")):
            save_config(test_config)
            
            # Check that the file was opened for writing
            mock_file.assert_called_once_with(Path("/mock/path/.unfckrc"), "w")
            
            # Check that write was called (we don't check the exact content as it depends on ConfigParser's formatting)
            self.assertTrue(mock_file().write.called)


if __name__ == "__main__":
    unittest.main()
