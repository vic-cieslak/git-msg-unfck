#!/usr/bin/env python3

import os
import sys
from typing import List, Dict, Any, Optional

try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    COLOR_SUPPORT = True
except ImportError:
    COLOR_SUPPORT = False

from .git_utils import get_commit_info, rewrite_commit_message, is_shared_branch
from .llm_providers import get_improved_message


def colorize(text: str, color: str) -> str:
    """Add color to text if color support is available."""
    if not COLOR_SUPPORT:
        return text
    
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "reset": Style.RESET_ALL,
    }
    
    return f"{colors.get(color, '')}{text}{colors.get('reset', '')}"


def prompt_for_reason(commit_hash: str) -> str:
    """Prompt the user for the reason behind a commit."""
    print(f"\nCommit: {commit_hash[:7]}")
    return input("Why did you make this change? (optional): ").strip()


def display_commit_info(
    commit_hash: str,
    original_message: str,
    author: str,
    diff: str,
    show_diff: bool = True,
) -> None:
    """Display information about a commit."""
    print(f"\n{colorize('Commit:', 'cyan')} {commit_hash[:7]}")
    print(f"{colorize('Author:', 'cyan')} {author}")
    print(f"{colorize('Original message:', 'cyan')} {original_message}")
    
    if show_diff:
        print(f"\n{colorize('Diff:', 'cyan')}")
        # Limit diff to a reasonable size for display
        max_diff_lines = 20
        diff_lines = diff.split("\n")
        if len(diff_lines) > max_diff_lines:
            print("\n".join(diff_lines[:max_diff_lines]))
            print(f"... {len(diff_lines) - max_diff_lines} more lines ...")
        else:
            print(diff)


def prompt_for_action(original_message: str, improved_message: str) -> str:
    """Prompt the user for action on the improved message."""
    print(f"\n{colorize('Original:', 'yellow')} {original_message}")
    print(f"{colorize('Improved:', 'green')} {improved_message}")
    
    while True:
        choice = input(f"\n{colorize('Accept?', 'cyan')} [y/n/e=edit/s=skip]: ").lower()
        if choice in ["y", "n", "e", "s"]:
            return choice
        print("Invalid choice. Please enter y, n, e, or s.")


def clean_message(message: str) -> str:
    """Remove unnecessary quotes and formatting from commit messages."""
    # Remove surrounding quotes if present
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    return message


def edit_message(message: str) -> str:
    """Allow the user to edit a message."""
    # Create a temporary file with the message
    import tempfile
    import subprocess
    
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as f:
        f.write(message)
        temp_file = f.name
    
    # Open the file in the user's preferred editor
    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, temp_file], check=True)
    except subprocess.CalledProcessError:
        print("Error opening editor. Using default message.")
        return message
    
    # Read the edited message
    with open(temp_file, "r") as f:
        edited_message = f.read().strip()
    
    # Clean up
    os.unlink(temp_file)
    
    return edited_message


def process_commits(
    commit_hashes: List[str],
    auto_apply: bool = False,
    ask_why: bool = False,
    global_why: Optional[str] = None,
    model: str = "gpt-4",
    dry_run: bool = False,
    config: Dict[str, Any] = None,
) -> None:
    """Process a list of commits to improve their messages."""
    if not commit_hashes:
        print("No commits to process")
        return
    
    # Check if we're operating on a shared branch
    if (
        config.get("behavior", {}).get("warn_on_shared_branches", True)
        and not dry_run
        and not auto_apply
        and is_shared_branch()
    ):
        print(colorize(
            "Warning: You are about to modify commit messages on a shared branch. "
            "This can cause problems for other developers. "
            "Consider creating a new branch first.",
            "yellow"
        ))
        choice = input("Continue? [y/N]: ").lower()
        if choice != "y":
            print("Aborting.")
            return
    
    # Get the API key from config
    api_key = config.get("provider", {}).get("api_key")
    
    # Get a global reason if ask_why is true and we have multiple commits
    shared_reason = global_why
    if ask_why and len(commit_hashes) > 1:
        print(f"\nCommit: {commit_hashes[0][:7]} (and {len(commit_hashes)-1} more)")
        shared_reason = input("Why did you make these changes? (optional): ").strip()
    
    # Process each commit
    for commit_hash in commit_hashes:
        # Get commit information
        original_message, author, diff = get_commit_info(commit_hash)
        if not original_message or not diff:
            print(f"Error: Could not get information for commit {commit_hash[:7]}")
            continue
        
        # Display commit information
        display_commit_info(
            commit_hash,
            original_message,
            author,
            diff,
            show_diff=config.get("behavior", {}).get("show_diff", True),
        )
        
        # Get the reason for the commit
        reason = None
        if ask_why and len(commit_hashes) == 1:
            # Only prompt individually for a single commit
            reason = prompt_for_reason(commit_hash)
        else:
            reason = shared_reason
        
        # Generate improved message
        print(f"\nGenerating improved message using {model}...")
        improved_message = get_improved_message(
            diff,
            original_message,
            reason,
            model,
            api_key,
        )
        
        if not improved_message:
            print(colorize("Error: Could not generate improved message", "red"))
            continue
        
        # Clean the message by removing unnecessary quotes if configured
        if config.get("behavior", {}).get("remove_quotes", True):
            improved_message = clean_message(improved_message)
        
        # Handle the improved message
        if auto_apply:
            if dry_run:
                print(f"\n{colorize('Would apply:', 'green')} {improved_message}")
            else:
                print(f"\n{colorize('Applying:', 'green')} {improved_message}")
                if rewrite_commit_message(commit_hash, improved_message):
                    print(colorize("Successfully rewrote commit message", "green"))
                else:
                    print(colorize("Error: Failed to rewrite commit message", "red"))
        else:
            action = prompt_for_action(original_message, improved_message)
            
            if action == "y":
                if dry_run:
                    print(colorize("Would apply the improved message", "green"))
                else:
                    if rewrite_commit_message(commit_hash, improved_message):
                        print(colorize("Successfully rewrote commit message", "green"))
                    else:
                        print(colorize("Error: Failed to rewrite commit message", "red"))
            
            elif action == "e":
                edited_message = edit_message(improved_message)
                # Clean the edited message as well if configured
                if config.get("behavior", {}).get("remove_quotes", True):
                    edited_message = clean_message(edited_message)
                if dry_run:
                    print(f"\n{colorize('Would apply edited message:', 'green')} {edited_message}")
                else:
                    if rewrite_commit_message(commit_hash, edited_message):
                        print(colorize("Successfully rewrote commit message", "green"))
                    else:
                        print(colorize("Error: Failed to rewrite commit message", "red"))
            
            elif action == "n":
                print(colorize("Keeping original message", "yellow"))
            
            elif action == "s":
                print(colorize("Skipping this commit", "yellow"))
    
    print("\nDone!")
