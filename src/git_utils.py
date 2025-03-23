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


def is_head_commit(commit_hash: str) -> bool:
    """Check if the commit is the HEAD commit."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip() == commit_hash
    except Exception:
        return False


def is_root_commit(commit_hash: str) -> bool:
    """Check if the commit is the root commit (first commit in the repository)."""
    try:
        # Try to get the parent of the commit
        result = subprocess.run(
            ["git", "rev-parse", f"{commit_hash}^"],
            capture_output=True, text=True, check=False
        )
        # If the command fails, it's the root commit
        return result.returncode != 0
    except Exception:
        return False


def clean_filter_branch_backup():
    """Clean up the filter-branch backup refs."""
    try:
        # Check if the backup refs exist
        result = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname)", "refs/original/"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("Cleaning up filter-branch backup refs...")
            
            # Get the current branch name
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = branch_result.stdout.strip()
            
            # Delete the backup refs for the current branch
            if current_branch:
                subprocess.run(
                    ["git", "update-ref", "-d", f"refs/original/refs/heads/{current_branch}"],
                    check=False,
                    capture_output=True
                )
            
            # Also try to delete master/main backup refs
            for branch in ["master", "main"]:
                subprocess.run(
                    ["git", "update-ref", "-d", f"refs/original/refs/heads/{branch}"],
                    check=False,
                    capture_output=True
                )
            
            # Expire reflog and run garbage collection
            subprocess.run(
                ["git", "reflog", "expire", "--expire=now", "--all"],
                check=False,
                capture_output=True
            )
            subprocess.run(
                ["git", "gc", "--prune=now"],
                check=False,
                capture_output=True
            )
            print("Backup refs cleaned up")
    except Exception as e:
        print(f"Warning: Failed to clean up backup refs: {e}")


def rewrite_head_commit(new_message: str) -> bool:
    """Rewrite the HEAD commit message using git commit --amend."""
    try:
        print("Rewriting HEAD commit message using git commit --amend...")
        
        # Create a temporary file for the commit message
        message_file = os.path.join(os.getcwd(), ".git", "COMMIT_MSG")
        with open(message_file, "w") as f:
            f.write(new_message)
        
        # Amend the commit with the new message
        result = subprocess.run(
            ["git", "commit", "--amend", "-F", message_file, "--no-edit"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Clean up
        if os.path.exists(message_file):
            os.remove(message_file)
        
        print("Successfully rewrote HEAD commit message")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Git amend error (exit code {e.returncode}):")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        if e.stderr:
            print(f"Standard error: {e.stderr}")
        return False
    
    except Exception as e:
        print(f"Unexpected error rewriting HEAD commit message: {e}")
        return False


def rewrite_past_commit(commit_hash: str, new_message: str) -> bool:
    """Rewrite a past commit message using git filter-branch."""
    message_file = None
    
    try:
        print(f"Rewriting past commit message for {commit_hash[:7]} using git filter-branch...")
        
        # Create a temporary file for the commit message
        message_file = os.path.join(os.getcwd(), ".git", "COMMIT_MSG")
        with open(message_file, "w") as f:
            f.write(new_message)
        
        # Clean up any previous filter-branch backups to avoid errors
        clean_filter_branch_backup()
        
        # Create a filter command that replaces only the target commit's message
        filter_cmd = f'if [ "$GIT_COMMIT" = "{commit_hash}" ]; then cat {message_file}; else cat; fi'
        
        # Check if this is the root commit (first commit in the repository)
        is_root = is_root_commit(commit_hash)
        
        # For root commits, we need to use --root instead of commit_hash^..HEAD
        if is_root:
            print(f"Detected root commit {commit_hash[:7]}, using --root")
            range_arg = "--root"
        else:
            range_arg = f"{commit_hash}^..HEAD"
        
        # Use git filter-branch to rewrite the message (non-interactive)
        result = subprocess.run(
            [
                "git", "filter-branch", "--force", "--msg-filter", 
                filter_cmd,
                range_arg
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(f"Filter-branch output: {result.stdout}")
        
        # Clean up
        if os.path.exists(message_file):
            os.remove(message_file)
        
        print(f"Successfully rewrote commit message for {commit_hash[:7]}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Git filter-branch error (exit code {e.returncode}):")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        if e.stderr:
            print(f"Standard error: {e.stderr}")
        
        # Clean up any temporary files
        if message_file and os.path.exists(message_file):
            os.remove(message_file)
        
        return False
    
    except Exception as e:
        print(f"Unexpected error rewriting past commit message: {e}")
        
        # Clean up any temporary files
        if message_file and os.path.exists(message_file):
            os.remove(message_file)
        
        return False


def rewrite_commit_message(commit_hash: str, new_message: str) -> bool:
    """
    Rewrite a commit message.
    
    Uses different strategies based on whether the commit is the HEAD commit:
    - For HEAD commit: Uses git commit --amend (simple, fast)
    - For past commits: Uses git filter-branch (more complex but non-interactive)
    """
    print(f"Preparing to rewrite commit message for {commit_hash[:7]}...")
    
    # Check if this is the HEAD commit
    if is_head_commit(commit_hash):
        return rewrite_head_commit(new_message)
    else:
        return rewrite_past_commit(commit_hash, new_message)


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
