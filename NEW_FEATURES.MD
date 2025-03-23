# 🚀 Git-Msg-Unfck: Feature Roadmap & Improvements

> A comprehensive plan for enhancing the git-msg-unfck tool with new features and improvements.

This document outlines planned enhancements to make the tool more robust, user-friendly, and powerful.

---

## 🛠️ Current Issues

### 1. Git Push/Pull After Rewriting Commits

**Problem:** Rewriting commit history causes issues with remote repositories.

```
git push
To github.com:vic-cieslak/git-msg-unfck.git
 ! [rejected]        master -> master (non-fast-forward)
error: failed to push some refs to 'github.com:vic-cieslak/git-msg-unfck.git'
```

**Solution:**
- Add a `--force-push` option that automatically runs `git push --force` after rewriting
- Implement a safety check that warns users about shared branches
- Add documentation explaining the consequences of rewriting history
- Provide a `--backup` option to create a backup branch before rewriting

**Implementation:**
```python
# Add to CLI options
subparser.add_argument(
    "--force-push", action="store_true",
    help="Force push to remote after rewriting commit messages (use with caution)"
)

# In process_commits function
if args.force_push and not dry_run:
    print("Force pushing changes to remote...")
    subprocess.run(["git", "push", "--force"], check=False)
```

---

## ✨ Feature Enhancements

### 2. Remove Double Quotes from Commit Messages

**Problem:** Generated messages sometimes contain unnecessary quotes.

**Solution:**
- Add a post-processing step to clean up generated messages
- Implement a configurable message formatter

**Implementation:**
```python
def clean_message(message: str) -> str:
    """Remove unnecessary quotes and formatting from commit messages."""
    # Remove surrounding quotes if present
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    return message
```

### 3. "Why" Flag Improvements

**Problem:** The "why" context is valuable but optional.

**Solution:**
- Make `--ask-why` the default behavior for interactive mode
- Add a `--no-why` flag to skip the prompt
- Store common "why" reasons in config for reuse

**Implementation:**
```python
# Update defaults in config
config.get("defaults", {}).get("prompt_user_for_why", True)

# Add to CLI options
subparser.add_argument(
    "--no-why", action="store_true",
    help="Skip prompting for the reason behind commits"
)
```

### 4. Token Management

**Problem:** API token management is cumbersome.

**Solution:**
- Add dedicated commands for configuration
- Implement secure token storage
- Add token validation

**Implementation:**
```python
# New subcommands
config_parser = subparsers.add_parser("config", help="Configure the tool")
config_subparsers = config_parser.add_subparsers(dest="config_command")

# Set token command
token_parser = config_subparsers.add_parser("set-token", help="Set the OpenRouter API token")
token_parser.add_argument("token", help="Your OpenRouter API token")
```

### 5. Skip Meaningful Messages

**Problem:** Some commits already have good messages.

**Solution:**
- Add a quality detection algorithm
- Implement a `--min-quality` threshold
- Allow manual skipping in interactive mode

**Implementation:**
```python
def is_meaningful_message(message: str) -> bool:
    """Check if a commit message is already meaningful."""
    # Simple heuristics: length, presence of verbs, absence of generic terms
    if len(message) < 10:
        return False
    if message.lower() in ["fix", "update", "change", "wip", "commit"]:
        return False
    return True
```

### 6. Handle Large Diffs

**Problem:** Large diffs may exceed token limits or be too complex.

**Solution:**
- Implement diff summarization
- Add chunking for large diffs
- Provide file-level summaries instead of full diffs

**Implementation:**
```python
def summarize_diff(diff: str, max_tokens: int = 4000) -> str:
    """Summarize a large diff to fit within token limits."""
    if len(diff) <= max_tokens:
        return diff
        
    # Extract file names and stats
    files_changed = []
    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            files_changed.append(line)
            
    return "\n".join([
        f"Large diff summarized ({len(diff)} characters):",
        f"Files changed: {len(files_changed)}",
        *files_changed[:10],
        "..." if len(files_changed) > 10 else ""
    ])
```

### 7. Rename Consideration

**Options:**
- `git-msg-ai` - Clear, professional
- `git-msg-fixer` - Descriptive, less playful
- `commit-ai` - Simple, modern
- `git-msg-unfck` (current) - Memorable, casual

**Recommendation:** Keep current name for now, but offer a `--professional` flag that uses more formal language in outputs.

### 8. User Feedback System

**Solution:**
- Add a `--feedback` flag to rate message quality
- Implement telemetry (opt-in) to improve the system
- Create a feedback repository for issues

**Implementation:**
```python
# After displaying the improved message
if not auto_apply:
    feedback = input("Rate this message (1-5, or skip): ")
    if feedback.isdigit() and 1 <= int(feedback) <= 5:
        # Store feedback (locally or send to API if user opted in)
        pass
```

### 9. Fix Specific Commit by Hash

**Solution:**
- Add a new `commit` command that takes a hash

**Implementation:**
```python
# New subcommand
commit_parser = subparsers.add_parser("commit", help="Process a specific commit")
commit_parser.add_argument("hash", help="The commit hash to process")
```

---

## 💡 Additional Feature Ideas

### 10. Commit Message Templates
- Add support for conventional commits (feat, fix, docs, etc.)
- Allow custom templates in config
- Implement project-specific templates

### 11. Pre-commit Hook Integration
- Create a pre-commit hook that suggests better messages
- Add installation command: `unfck install-hooks`

### 12. Batch Processing with Different Models
- Allow processing different commits with different models
- Implement model fallback for rate limiting

### 13. Message Style Options
- Add `--style` flag with options like "concise", "detailed", "conventional"
- Customize prompt based on style

### 14. Local LLM Support
- Add support for local LLMs via API
- Implement offline mode with simpler heuristics

---

## 📋 Implementation Priority

1. Fix push/pull issues (critical)
2. Remove quotes from messages (quick win)
3. Improve "why" flag behavior (UX improvement)
4. Add specific commit processing (feature request)
5. Skip meaningful messages (efficiency)
6. Token management (usability)
7. Handle large diffs (robustness)
8. User feedback system (long-term improvement)
