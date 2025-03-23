# 🧠 git-msg-unfck

> If you're too lazy to write meaningful and useful commit messages while developing – this tool is for you.

`git-msg-unfck` rewrites your recent Git commit messages by analyzing the diffs and generating clean, descriptive messages using AI models like Claude 3.5/3.7, GPT-4, DeepSeek, or your own local LLM.

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

### Installation with Poetry

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/yourusername/git-msg-unfck.git
cd git-msg-unfck

# Install dependencies
poetry install

# Activate the Poetry shell (optional)
poetry shell
```

### Interactive dry-run mode (default)

```bash
# Within Poetry shell
unfck .

# Or without activating the shell
poetry run unfck .
```

### No confirmation, just rewrite

```bash
poetry run unfck . --just-fix-it
```

### Only fix last N commits

```bash
poetry run unfck last 2
```

### With specific model

```bash
poetry run unfck last 1 --model gpt-4
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
poetry run unfck . --all-branches
poetry run unfck . --only-main
```

### Providing context with --why

```bash
poetry run unfck last 3 --why "Fixing authentication bugs"
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
- name: Fix last 5 commit messages
  run: unfck last 5 --just-fix-it --model claude-3.5
  env:
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```

## 🖥️ Bash Alias

Add this to ~/.bashrc or ~/.zshrc:

```bash
alias unfck='python3 ~/tools/git-msg-unfck/unfck.py'
```

Then you can run:

```bash
unfck .
unfck . --just-fix-it
unfck last 3
```

## 🐳 Docker Usage

Run with Docker:

```bash
docker run -it --rm \
  -v $(pwd):/git \
  -e OPENROUTER_API_KEY=your-key \
  git-msg-unfck last 5 --model gpt-4
```

Or with docker-compose:

```bash
OPENROUTER_API_KEY=your-key docker-compose run git-msg-unfck last 3
```

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
