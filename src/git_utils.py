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
        
        # Handle 'last N' commits
        if args.last:
            count = int(args.last)
            commits = list(repo.iter_commits('HEAD', max_count=count))
            return [commit.hexsha for commit in commits]
        
        # Handle current branch
        if args.current_branch:
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
    try:
        # Create a temporary script for the rebase
        script_path = os.path.join(os.getcwd(), ".git", "rewrite-message.sh")
        with open(script_path, "w") as f:
            f.write(f"""#!/bin/sh
git commit --amend -m "{new_message}" --no-edit
""")
        os.chmod(script_path, 0o755)
        
        # Start an interactive rebase
        subprocess.run(
            ["git", "rebase", "-i", f"{commit_hash}^", "--exec", script_path],
            check=True,
        )
        
        # Clean up
        os.remove(script_path)
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Git rebase error: {e}")
        # Try to abort the rebase if it failed
        try:
            subprocess.run(["git", "rebase", "--abort"], check=False)
        except:
            pass
        return False
    except Exception as e:
        print(f"Error rewriting commit message: {e}")
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
