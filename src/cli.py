#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List, Optional

from .config import load_config
from .git_utils import get_commit_range, is_git_repo
from .message_generator import process_commits


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Improve Git commit messages using AI",
        prog="unfck"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # "." command for current branch
    current_parser = subparsers.add_parser(".", help="Process all commits in the current branch")

    # "last" command for processing last N commits
    last_parser = subparsers.add_parser("last", help="Process the last N commits")
    last_parser.add_argument("count", type=int, help="Number of commits to process")

    # Add common options to both subparsers
    for subparser in [current_parser, last_parser]:
        # Branch options
        branch_group = subparser.add_mutually_exclusive_group()
        branch_group.add_argument(
            "--all-branches", action="store_true",
            help="Process commits across all branches"
        )
        branch_group.add_argument(
            "--only-main", action="store_true",
            help="Process commits only on the main/master branch"
        )
        
        # Behavior options
        subparser.add_argument(
            "--just-fix-it", action="store_true",
            help="Automatically apply changes without confirmation"
        )
        subparser.add_argument(
            "--ask-why", action="store_true",
            help="Prompt for the reason behind each commit"
        )
        subparser.add_argument(
            "--why", type=str,
            help="Provide a global reason for all commits"
        )
        subparser.add_argument(
            "--model", type=str,
            help="Specify the AI model to use (e.g., gpt-4, claude-3.5)"
        )
        subparser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would be done without making changes"
        )

    return parser.parse_args(args)


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    # No validation needed for count as it's already enforced as int by argparse
    pass


def main() -> None:
    """Main entry point for the CLI."""
    # Load configuration
    config = load_config()

    # Parse command line arguments
    args = parse_args(sys.argv[1:])
    validate_args(args)

    # Check if we're in a Git repository
    if not is_git_repo():
        print("Error: Not a Git repository")
        sys.exit(1)

    # Determine the commit range to process
    commit_range = get_commit_range(args, config)
    if not commit_range:
        print("No commits to process")
        sys.exit(0)

    # Process the commits
    process_commits(
        commit_range,
        auto_apply=args.just_fix_it or config.get("defaults", {}).get("auto_apply", False),
        ask_why=args.ask_why or config.get("defaults", {}).get("prompt_user_for_why", False),
        global_why=args.why,
        model=args.model or config.get("provider", {}).get("engine", "gpt-4"),
        dry_run=args.dry_run,
        config=config
    )


if __name__ == "__main__":
    main()
