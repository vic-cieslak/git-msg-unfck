#!/usr/bin/env python3

import os
import subprocess
from typing import List, Dict, Any, Optional, Tuple

import git


def is_git_repo() -> bool:
    """Check if the current directory is a Git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_commit_range(args: Any, config: Dict[str, Any]) -> List[str]:
    """Get the range of commits to process based on command line arguments."""
    try:
        repo = git.Repo(os.getcwd())
        
        # Handle command selection
        if args.command == "last":
            # Handle 'last N' commits
            count = args.count
            commits = list(repo.iter_commits('HEAD', max_count=count))
            return [commit.hexsha for commit in commits]
        
        elif args.command == ".":
            # Handle current branch
            # Get the current branch name
            branch_name = repo.active_branch.name
            
            # Get the merge base with the main branch (usually 'main' or 'master')
            main_branch = 'main' if 'main' in repo.heads else 'master'
            try:
                merge_base = repo.git.merge_base(branch_name, main_branch)
                # Get all commits between merge_base and HEAD
                commits = list(repo.iter_commits(f'{merge_base}..HEAD'))
                return [commit.hexsha for commit in commits]
            except git.GitCommandError:
                # If there's an error (e.g., no common ancestor), just get all commits in the branch
                commits = list(repo.iter_commits(branch_name))
                return [commit.hexsha for commit in commits]
        
        # Handle all branches
        if args.all_branches:
            # Get all commits in the repository
            commits = list(repo.iter_commits('--all'))
            return [commit.hexsha for commit in commits]
        
        # Handle only main branch
        if args.only_main:
            main_branch = 'main' if 'main' in repo.heads else 'master'
            commits = list(repo.iter_commits(main_branch))
            return [commit.hexsha for commit in commits]
        
        # Default: use the last N commits specified in config
        default_count = config.get("defaults", {}).get("default_commit_count", 5)
        commits = list(repo.iter_commits('HEAD', max_count=default_count))
        return [commit.hexsha for commit in commits]
    
    except git.GitCommandError as e:
        print(f"Git error: {e}")
        return []
    except Exception as e:
        print(f"Error getting commit range: {e}")
        return []


def get_commit_info(commit_hash: str) -> Tuple[str, str, str]:
    """Get the commit message, author, and diff for a given commit hash."""
    try:
        repo = git.Repo(os.getcwd())
        commit = repo.commit(commit_hash)
        
        # Get the commit message
        message = commit.message.strip()
        
        # Get the author
        author = f"{commit.author.name} <{commit.author.email}>"
        
        # Get the diff
        diff = repo.git.show(commit_hash, format="")
        
        return message, author, diff
    
    except git.GitCommandError as e:
        print(f"Git error: {e}")
        return "", "", ""
    except Exception as e:
        print(f"Error getting commit info: {e}")
        return "", "", ""


def rewrite_commit_message(commit_hash: str, new_message: str) -> bool:
    """Rewrite the commit message for a given commit hash using git rebase."""
    message_file = None
    script_path = None
    
    try:
        print(f"Preparing to rewrite commit message for {commit_hash[:7]}...")
        
        # Create a temporary file for the commit message
        message_file = os.path.join(os.getcwd(), ".git", "COMMIT_MSG")
        with open(message_file, "w") as f:
            f.write(new_message)
        print(f"Commit message saved to temporary file: {message_file}")
        
        # Create a temporary script for the rebase
        script_path = os.path.join(os.getcwd(), ".git", "rewrite-message.sh")
        with open(script_path, "w") as f:
            f.write(f"""#!/bin/sh
git commit --amend -F "{message_file}" --no-edit
""")
        os.chmod(script_path, 0o755)
        print(f"Rebase script created: {script_path}")
        
        # Start an interactive rebase
        print(f"Starting interactive rebase for commit {commit_hash[:7]}...")
        result = subprocess.run(
            ["git", "rebase", "-i", f"{commit_hash}^", "--exec", script_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(f"Rebase output: {result.stdout}")
        
        # Clean up
        print("Cleaning up temporary files...")
        if os.path.exists(script_path):
            os.remove(script_path)
        if os.path.exists(message_file):
            os.remove(message_file)
        
        print(f"Successfully rewrote commit message for {commit_hash[:7]}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Git rebase error (exit code {e.returncode}):")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        if e.stderr:
            print(f"Standard error: {e.stderr}")
        
        # Try to abort the rebase if it failed
        print("Attempting to abort the rebase...")
        try:
            abort_result = subprocess.run(
                ["git", "rebase", "--abort"],
                capture_output=True,
                text=True
            )
            if abort_result.returncode == 0:
                print("Rebase aborted successfully")
            else:
                print(f"Failed to abort rebase: {abort_result.stderr}")
        except Exception as abort_error:
            print(f"Error aborting rebase: {abort_error}")
        
        # Clean up any temporary files
        try:
            if script_path and os.path.exists(script_path):
                os.remove(script_path)
            if message_file and os.path.exists(message_file):
                os.remove(message_file)
        except OSError as cleanup_error:
            print(f"Error cleaning up temporary files: {cleanup_error}")
        
        return False
    
    except Exception as e:
        print(f"Unexpected error rewriting commit message: {e}")
        
        # Clean up any temporary files
        try:
            if script_path and os.path.exists(script_path):
                os.remove(script_path)
            if message_file and os.path.exists(message_file):
                os.remove(message_file)
        except OSError:
            pass  # Ignore cleanup errors at this point
        
        return False


def is_shared_branch() -> bool:
    """Check if the current branch is shared with a remote repository."""
    try:
        repo = git.Repo(os.getcwd())
        branch_name = repo.active_branch.name
        
        # Check if the branch exists on any remote
        for remote in repo.remotes:
            remote_refs = [ref.name for ref in remote.refs]
            if f"refs/remotes/{remote.name}/{branch_name}" in remote_refs:
                return True
        
        return False
    
    except git.GitCommandError:
        # If there's an error, assume it's not shared to be safe
        return False
    except Exception:
        return False
