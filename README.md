# 🧠 git-msg-unfck

> I commit often, but writing proper messages slows me down or gets neglected..

`git-msg-unfck` rewrites your recent Git commit messages by analyzing the diffs and generating clean, descriptive messages using AI models like Claude 3.5/3.7, GPT-4, DeepSeek, or your own local LLM.

## 📦 Installation

### Quick Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/git-msg-unfck.git
cd git-msg-unfck

# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Build the package
poetry build

# Install the built package
pip install dist/git_msg_unfck-0.1.0.tar.gz
```

After installation, the `unfck` command will be available in your terminal.

### Future PyPI Installation (Coming Soon)

```bash
# This method is not yet available
pip install git-msg-unfck
```

---

## 💡 What It Does

- 📄 Analyzes `git diff` for each of your last commits
- 🤖 Asks an LLM to explain the changes and rewrite the commit message
- ❓ Optionally asks you *why* you made the change
- ✅ Lets you approve suggestions interactively
- 🛠️ Can automatically rewrite messages using `git rebase`

---

## ✨ Features

- 🔍 Fix messages for N last commits or the entire branch
- 📦 Supports GPT-4, Claude, DeepSeek, local LLMs (via OpenRouter)
- 🧑‍💻 Interactive mode (dry-run with confirmation)
- 🤖 Fully automated mode (`--just-fix-it`)
- 🌿 Multi-branch and CI/CD support
- 🧩 Configurable via `.unfckrc`

---

## 🚀 Quick Usage

### Interactive dry-run mode (default)

Please in all commands with unfck pass OPENROUTER TOKEN like this:
(to be improved)

```bash
OPENROUTER_API_KEY=sk.... unfck
```

```bash
# Process all commits in the current branch
unfck
```

### No confirmation, just rewrite

```bash
unfck --just-fix-it
```

### Only fix last N commits

```bash
unfck last 2
```

### Process first N commits (oldest first)

```bash
unfck first 5
```

### With specific model

```bash
unfck last 1 --model gpt-4
```

### Available models

OpenRouter supports various models including:
```
gpt-4
gpt-3.5-turbo
claude-3-opus
claude-3-sonnet
claude-3-haiku
```

### Across branches

```bash
unfck --all-branches
unfck --only-main
```

### Providing context with --why

```bash
# Provide a global reason for all commits
unfck last 3 --why "Fixing authentication bugs"

# Interactively prompt for a reason (once for multiple commits)
unfck last 3 --ask-why
```

## 🔧 Configuration

Add a config file at ~/.unfckrc:

```ini
[provider]
engine = gpt-4
api_key = YOUR_OPENROUTER_KEY

[defaults]
auto_apply = false
prompt_user_for_why = true
```

You can also override settings via CLI flags.

## 🧠 How It Works

1. Finds commits via git rev-list
2. For each commit:
   - Gets git diff and current message
   - Optionally asks you "Why did you make this change?"
   - Sends everything to the AI model
   - Receives and displays improved commit message
3. If accepted:
   - Uses git rebase -i or git commit --amend to replace message

## ⚙️ Supported Models

All accessed via OpenRouter:

- GPT-4
- Claude 3.5 / 3.7
- DeepSeek
- Local models (if routed via OpenRouter or API endpoint)

## 🧪 In CI/CD

Run automatically in pipelines:

```yaml
- name: Clone repository
  uses: actions/checkout@v3
  with:
    repository: vic-cieslak/git-msg-unfck
    path: git-msg-unfck

- name: Install Poetry
  run: curl -sSL https://install.python-poetry.org | python3 -

- name: Build and install git-msg-unfck
  run: |
    cd git-msg-unfck
    poetry build
    pip install dist/git_msg_unfck-0.1.0.tar.gz

- name: Fix last 5 commit messages
  run: unfck last 5 --just-fix-it --model claude-3.5
  env:
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```


## 🐳 Docker Usage (Limited)

> **Note**: Docker support has limitations. The tool will only operate on the Git repository that's mounted to the container. You cannot specify an external Git repository path like `/home/user/Git_repo` as the tool is designed to work only with the current working directory mounted at `/git` in the container.

<!-- 
Docker support is currently limited and commented out until full path support is implemented.

You can use the provided Dockerfile to build and run the tool:

```dockerfile
FROM python:3.10-slim

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Build and install the package
RUN poetry build && pip install dist/git_msg_unfck-0.1.0.tar.gz

# Set working directory for Git repositories
WORKDIR /git

# Default command
ENTRYPOINT ["unfck"]
```

Build and run:

```bash
# Build the Docker image
docker build -t git-msg-unfck .

# Run with Docker
docker run -it --rm \
  -v $(pwd):/git \
  -e OPENROUTER_API_KEY=your-key \
  git-msg-unfck last 5 --model gpt-4
```

Or use the provided docker-compose.yml:

```bash
OPENROUTER_API_KEY=your-key docker-compose run git-msg-unfck last 3
```
-->

## 🧪 Testing

### Quick Test on Current Repository

To quickly test the tool on your current repository, use the provided script:

```bash
# Make the script executable if needed
chmod +x test-current-repo.sh

# Run the test script with your OpenRouter API key
OPENROUTER_API_KEY=your_key ./test-current-repo.sh
```

This will run the tool on the last commit in your current repository and show you the before and after commit messages.

### Integration Tests

The project includes integration tests that create a temporary Git repository, make commits with poor messages, and test the ability to improve them using the real OpenRouter API.

To run the integration tests:

```bash
# Set the API key as an environment variable
export OPENROUTER_API_KEY=your_openrouter_api_key

# Run the test
unfck-test

# Or provide the API key directly
unfck-test --api-key your_openrouter_api_key
```

Note: These tests make real API calls to OpenRouter using Claude 3.7, which will incur costs.

## 🛣️ Roadmap

- Pre-commit hook integration
- PR title/description generation
- Model fallback logic
- Local LLM CLI support
- Message tone: concise / formal / playful

## 🙈 Note on Rewriting

This tool modifies Git history using git rebase. Use it on safe branches, not shared ones, unless you know what you're doing.

## 📜 License

MIT
