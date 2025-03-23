#!/usr/bin/env python3

import os
import shutil
import subprocess
import tempfile
import unittest
import argparse
from pathlib import Path

class GitMsgUnfckIntegrationTest(unittest.TestCase):
    def setUp(self):
        # Get API key from environment or argument
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable must be set")
        
        # Create a temporary directory for the test repository
        self.test_dir = tempfile.mkdtemp()
        self.old_dir = os.getcwd()
        
        # Initialize a new Git repository
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Create test files and make commits with poor messages
        self._create_test_commits()
        
        # Path to the project directory
        self.project_dir = self.old_dir
    
    def tearDown(self):
        # Clean up
        os.chdir(self.old_dir)
        shutil.rmtree(self.test_dir)
    
    def _create_test_commits(self):
        # Create a file and make a commit with a poor message
        with open("file1.txt", "w") as f:
            f.write("Initial content")
        
        subprocess.run(["git", "add", "file1.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "stuff"], check=True)
        
        # Make another change and commit
        with open("file1.txt", "a") as f:
            f.write("\nMore content with a bug fix")
        
        subprocess.run(["git", "add", "file1.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "fix"], check=True)
        
        # Create another file and commit
        with open("file2.txt", "w") as f:
            f.write("Another file with important functionality")
        
        subprocess.run(["git", "add", "file2.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "asdf"], check=True)
    
    def test_unfck_last_commit(self):
        """Test improving the last commit message."""
        print("\n\nTesting improvement of last commit message...")
        
        # Run unfck on the last commit with Claude 3.7 using Poetry
        os.chdir(self.project_dir)  # Change to project directory to use Poetry
        result = subprocess.run(
            [
                "poetry", "run", "unfck", 
                "last", "1", 
                "--just-fix-it",
                "--model", "anthropic/claude-3-7-sonnet-20240229"
            ],
            env={**os.environ, "OPENROUTER_API_KEY": self.api_key},
            capture_output=True,
            text=True
        )
        os.chdir(self.test_dir)  # Change back to test directory
        
        # Print the output for debugging
        print(f"Command output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        
        # Check that the command succeeded
        self.assertEqual(result.returncode, 0, f"Command failed with: {result.stderr}")
        
        # Get the new commit message
        log_result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            check=True
        )
        
        new_message = log_result.stdout.strip()
        print(f"Original message: 'asdf'")
        print(f"New message: '{new_message}'")
        
        # Verify the message was improved (not just "asdf")
        self.assertNotEqual(new_message, "asdf")
        self.assertTrue(len(new_message) > 10)  # Arbitrary length check
    
    def test_unfck_with_why(self):
        """Test improving a commit message with a 'why' reason."""
        print("\n\nTesting improvement with 'why' context...")
        
        # Run unfck on the second commit with a 'why' reason using Poetry
        os.chdir(self.project_dir)  # Change to project directory to use Poetry
        result = subprocess.run(
            [
                "poetry", "run", "unfck", 
                "last", "2", 
                "--just-fix-it",
                "--model", "anthropic/claude-3-7-sonnet-20240229",
                "--why", "Fixing a critical bug in the authentication flow"
            ],
            env={**os.environ, "OPENROUTER_API_KEY": self.api_key},
            capture_output=True,
            text=True
        )
        os.chdir(self.test_dir)  # Change back to test directory
        
        # Print the output for debugging
        print(f"Command output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        
        # Check that the command succeeded
        self.assertEqual(result.returncode, 0, f"Command failed with: {result.stderr}")
        
        # Get the new commit message
        log_result = subprocess.run(
            ["git", "log", "-2", "--pretty=%B", "--skip=1"],
            capture_output=True,
            text=True,
            check=True
        )
        
        new_message = log_result.stdout.strip()
        print(f"Original message: 'fix'")
        print(f"New message: '{new_message}'")
        
        # Verify the message was improved and includes context about authentication
        self.assertNotEqual(new_message, "fix")
        self.assertTrue(len(new_message) > 10)
        # The message should ideally mention authentication, but this is not guaranteed
        # as it depends on the LLM's response


def parse_args():
    parser = argparse.ArgumentParser(description="Run integration tests for git-msg-unfck")
    parser.add_argument("--api-key", help="OpenRouter API key (can also use OPENROUTER_API_KEY env var)")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.api_key:
        os.environ["OPENROUTER_API_KEY"] = args.api_key
    
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Error: OpenRouter API key must be provided via --api-key or OPENROUTER_API_KEY env var")
        return 1
    
    # Check if Poetry is installed
    try:
        subprocess.run(["poetry", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Poetry is not installed")
        print("Please install Poetry: curl -sSL https://install.python-poetry.org | python3 -")
        return 1
    
    # Ensure dependencies are installed
    print("Ensuring dependencies are installed...")
    try:
        subprocess.run(["poetry", "install"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies with Poetry")
        return 1
    
    unittest.main(argv=['first-arg-is-ignored'])

if __name__ == "__main__":
    main()
