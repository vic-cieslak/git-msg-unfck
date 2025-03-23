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

### Interactive dry-run mode (default)

```bash
unfck .
```

### No confirmation, just rewrite

```bash
unfck . --just-fix-it
```

### Only fix last N commits

```bash
unfck last 2
```

### Across branches

```bash
unfck --all-branches
unfck --only-main
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
