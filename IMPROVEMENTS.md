## 🎯 Tool Overview: Purpose & Goals

### Core Idea:
> A CLI tool that rewrites Git commit messages by analyzing `git diff` and applying an LLM like Claude 3.5, GPT-4, or DeepSeek for smart, descriptive commit messages.

### Target Audience:
- Developers who care about clean history
- Teams with enforced commit standards
- Solo hackers who want good logs without the effort
- OSS maintainers who want polished PRs

### Pain Point Solved:
> “I commit often, but writing proper messages slows me down or gets neglected.”

---

## 🛠️ How Should It Be Made?

### 1. **CLI-first Tool with Pipx Support**
- **Install**: `pipx install commit-sage` or `pip install .`
- **Run**: `commit-sage fix HEAD~5` or `commit-sage review`
- Use `click` or `typer` for CLI ergonomics

### 2. **LLM Integration (pluggable)**
- Supports:
  - `gpt-4` (OpenAI)
  - `claude-3.5` (Anthropic)
  - `deepseek-coder` or local LLM
- `.commit-sage.toml` or `.commitrc` for config:
  ```toml
  [llm]
  provider = "openai"
  model = "gpt-4"
  api_key = "env:OPENAI_API_KEY"
  ```

### 3. **Modes of Operation**
- `fix HEAD`: Rewrite latest commit
- `fix HEAD~10`: Rewrite last 10 commits
- `review`: Show suggestions, let user pick one
- `apply`: Use rebase to apply improved messages

Optional:
- `--interactive`: Show before/after for confirmation
- `--dry-run`: Preview changes
- `--json`: Output raw LLM results

### 4. **Zero Lock-in**
- No server needed (unless user wants hosted inference)
- Use `git diff`, `git log`, `git rebase` under the hood
- Doesn’t modify code — only messages

---

## 🧠 LLM Prompt Design

Good prompts are everything here.

Example:
```text
You are a Git expert helping improve commit messages.
Analyze the following Git diff and produce a concise, clear, and professional commit message.

Git diff:
<...>

Output format: Just the commit message, no commentary.
```

You can add `--style friendly`, `--style conventional`, `--style emoji` to offer flavor.

---

## 💬 UX Example

```bash
$ commit-sage fix HEAD~3 --interactive
[1/3] Suggested: "refactor(user): simplify password reset flow"
Keep this message? (Y/n/edit)
```

Or go full automatic:

```bash
$ commit-sage fix HEAD~10 --apply
✅ All 10 commit messages rewritten with GPT-4
```

---

## 💡 Bonus Features (Future)
- `pre-commit` hook support
- VSCode extension
- Pull Request summarizer
- Conventional Commit validation

---

## 🚀 Name Suggestion for Launch

Your shortlist is solid, but if you're aiming for professional, memorable, and future-safe:

### **Top Choice: `commit-sage`**
- Clean, dev-friendly
- Hints at AI, wisdom
- CLI command: `commit-sage fix`

Other solid runner-ups:
- `git-msg-maestro`
- `commit-craft`
- `git-msg-ai`

