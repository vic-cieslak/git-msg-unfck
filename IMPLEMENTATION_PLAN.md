# Git-Msg-Unfck Implementation Plan

## Project Overview

`git-msg-unfck` is a CLI tool that improves Git commit messages by:
- Analyzing git diffs from previous commits
- Using AI models (via OpenRouter) to generate better messages
- Optionally prompting for the "why" behind changes
- Supporting both interactive and automatic modes
- Working across branches and in CI/CD pipelines

## Project Structure

```
git-msg-unfck/
├── README.md                 # Project documentation
├── IMPLEMENTATION_PLAN.md    # This document
├── unfck.py                  # Main CLI entry point
├── setup.py                  # For pip installation
├── requirements.txt          # Dependencies
├── .unfckrc.example          # Example config file
├── Dockerfile                # For containerized usage
├── docker-compose.yml        # For easy Docker deployment
├── .github/                  # GitHub Actions workflows
├── src/
│   ├── __init__.py
│   ├── git_utils.py          # Git operations (diff, rebase, etc.)
│   ├── llm_providers.py      # OpenRouter integration
│   ├── message_generator.py  # Prompt engineering & message creation
│   ├── config.py             # Configuration management
│   └── cli.py                # Command parsing logic
└── tests/                    # Unit tests
```

## Core Components

### 1. Git Operations (`src/git_utils.py`)
- Extract diffs from specified commits
- Get original commit messages
- Handle rebase operations to rewrite history
- Support branch operations

### 2. LLM Integration (`src/llm_providers.py`)
- OpenRouter API client
- Model selection (GPT-4, Claude, DeepSeek)
- Prompt construction with diff + context
- Response parsing

### 3. CLI Interface (`src/cli.py` and `unfck.py`)
- Command structure: `unfck [options] <target>`
- Key flags:
  - `--just-fix-it`: No confirmation, just rewrite
  - `--ask-why`: Prompt for reasoning
  - `--why "reason"`: Provide global reason
  - `--model model-name`: Select AI model
  - `--all-branches` / `--only-main`: Branch selection

### 4. Configuration (`src/config.py`)
- Config file at `~/.unfckrc`
- Environment variables for API keys
- Command-line overrides

### 5. Docker Support
- Containerized execution
- Volume mounting for Git repositories
- Environment variable configuration
- CI/CD integration

## Implementation Steps

### Phase 1: Core Functionality
1. **Setup Project Skeleton**
   - Create directory structure
   - Initialize git repo
   - Set up basic CLI with argparse

2. **Git Utilities**
   - Implement commit history retrieval
   - Extract diffs and messages
   - Set up rebase operations

3. **LLM Integration**
   - Implement OpenRouter API client
   - Create prompt templates
   - Handle response parsing

### Phase 2: User Experience
4. **User Interaction**
   - Interactive confirmation flow
   - "Why" prompting mechanism
   - Output formatting

5. **Configuration Management**
   - Config file parsing
   - Environment variable support
   - Command-line override logic

### Phase 3: Deployment & Distribution
6. **Docker Support**
   - Create Dockerfile
   - Set up docker-compose.yml
   - Document Docker usage

7. **CI/CD Integration**
   - GitHub Actions workflow
   - Automated testing
   - Example pipeline configurations

8. **Testing & Documentation**
   - Unit tests for core functionality
   - Update README with examples
   - Create example config

## Docker Implementation

### Dockerfile
```dockerfile
FROM python:3.10-slim

# Install git
RUN apt-get update && apt-get install -y git && apt-get clean

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create volume mount point for git repositories
VOLUME /git

# Set working directory to mounted git repo
WORKDIR /git

# Set entrypoint
ENTRYPOINT ["unfck"]
```

### Docker Usage
```bash
# Run with current directory mounted
docker run -it --rm \
  -v $(pwd):/git \
  -e OPENROUTER_API_KEY=your-key \
  git-msg-unfck last 5 --model gpt-4
```

### docker-compose.yml
```yaml
version: '3'
services:
  git-msg-unfck:
    build: .
    volumes:
      - .:/git
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
```

## Key Technical Decisions

1. **Language & Dependencies**
   - Python 3.8+ for broad compatibility
   - Minimal dependencies: requests, gitpython
   - No complex frameworks

2. **Git Operations**
   - Use GitPython for repo operations
   - Fall back to subprocess for complex git commands

3. **API Integration**
   - OpenRouter for model flexibility
   - Support for API keys via env vars and config

4. **User Experience**
   - Default to interactive mode (safe)
   - Clear, colorful terminal output
   - Sensible defaults with override options

5. **Docker Strategy**
   - Slim Python base image
   - Volume mounting for Git repositories
   - Environment variables for configuration
   - Simple entrypoint for direct usage

## Challenges & Considerations

1. **Git History Rewriting**
   - Ensure safety measures for shared branches
   - Clear warnings about history rewriting

2. **API Key Management**
   - Secure handling of API keys
   - Support for different authentication methods

3. **Docker Git Integration**
   - Proper handling of Git credentials in container
   - Ensuring Git operations work correctly with mounted volumes

4. **Error Handling**
   - Graceful handling of API failures
   - Clear error messages for Git operations

## Timeline

1. **Phase 1 (Core Functionality)**: 1-2 days
2. **Phase 2 (User Experience)**: 1-2 days
3. **Phase 3 (Deployment & Distribution)**: 1-2 days

Total estimated time: 3-6 days depending on complexity and testing requirements.
