# How to Publish git-msg-unfck to PyPI.org

This guide provides step-by-step instructions for publishing the `git-msg-unfck` package to PyPI.org, making it available for installation via pip.

## Step 1: Prepare Your Package

Before publishing, ensure your package is ready:

1. **Update package metadata in pyproject.toml**:
   - Verify your package version (currently 0.1.0)
   - Update author information (replace placeholder email)
   - Update repository and homepage URLs (replace "yourusername")
   - Make sure description and keywords are accurate

   Example of updated metadata:
   ```toml
   [tool.poetry]
   name = "git-msg-unfck"
   version = "0.1.0"
   description = "A CLI tool to improve Git commit messages using AI"
   authors = ["Your Name <your.real.email@example.com>"]
   readme = "README.md"
   packages = [{include = "src"}]
   license = "MIT"
   repository = "https://github.com/your-actual-username/git-msg-unfck"
   homepage = "https://github.com/your-actual-username/git-msg-unfck"
   ```

2. **Ensure your README.md is complete**:
   - Clear installation instructions
   - Good usage examples
   - All features documented

3. **Check MANIFEST.in**:
   - Make sure it includes all non-Python files that should be in the package

## Step 2: Create a PyPI Account

1. Register at https://pypi.org/account/register/ if you don't have an account
2. Verify your email address

## Step 3: Generate an API Token

1. Log in to PyPI
2. Go to Account Settings → API tokens
3. Create a new API token with scope "Entire account" or limited to this project
4. **IMPORTANT**: Save this token securely - you won't be able to see it again!

## Step 4: Configure Poetry with Your PyPI Credentials

```bash
poetry config pypi-token.pypi your-api-token
```

## Step 5: Build Your Package

1. Make sure you're in the project root directory
2. Run:
   ```bash
   poetry build
   ```
3. This creates distribution files in the `dist/` directory:
   - A `.whl` file (wheel, binary distribution)
   - A `.tar.gz` file (source distribution)

## Step 6: Test Your Package Locally (Recommended)

Before publishing, test that your package installs and works correctly:

```bash
# Create a virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install your package from the local wheel
pip install dist/git_msg_unfck-0.1.0-py3-none-any.whl

# Test that it works
unfck --help
```

## Step 7: Publish to PyPI

Once you've verified everything works:

```bash
# Build and publish in one step
poetry publish --build

# Or if you've already built the package:
poetry publish
```

You'll see output indicating the upload progress and success.

## Step 8: Verify Your Package on PyPI

1. Visit https://pypi.org/project/git-msg-unfck/
2. Check that all metadata, README, and other information appears correctly
3. Try installing it from PyPI:
   ```bash
   pip install git-msg-unfck
   ```

## Optional: Test with TestPyPI First

If you want to practice or test the publishing process without affecting the real PyPI:

1. Register at https://test.pypi.org/account/register/
2. Generate a TestPyPI token
3. Configure Poetry:
   ```bash
   poetry config repositories.testpypi https://test.pypi.org/legacy/
   poetry config pypi-token.testpypi your-test-pypi-token
   ```
4. Publish to TestPyPI:
   ```bash
   poetry publish -r testpypi
   ```
5. Install from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ git-msg-unfck
   ```

## Updating Your Package

When you need to publish a new version:

1. Update the version in `pyproject.toml`:
   ```toml
   [tool.poetry]
   version = "0.1.1"  # Increment appropriately
   ```
2. Make your code changes
3. Build and publish as described above

## Automating with GitHub Actions

You can automate publishing with GitHub Actions. Create a workflow file at `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
    - name: Build and publish
      env:
        POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        poetry build
        poetry publish
```

With this workflow, a new package will be published automatically when you create a new release on GitHub.

## Common Issues and Solutions

1. **Name conflicts**: If the name is already taken on PyPI, you'll need to choose a different name
2. **Missing dependencies**: Ensure all dependencies are correctly listed in pyproject.toml
3. **README rendering issues**: Make sure your README.md uses valid Markdown that PyPI can render
4. **Version conflicts**: You cannot upload the same version twice to PyPI - always increment the version

## Semantic Versioning

When updating your package version, follow semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Incompatible API changes
- MINOR: Add functionality in a backward-compatible manner
- PATCH: Backward-compatible bug fixes

For example:
- 0.1.0 → 0.1.1: Bug fixes
- 0.1.0 → 0.2.0: New features, no breaking changes
- 0.1.0 → 1.0.0: Stable release or breaking changes

## Package Maintenance Best Practices

1. **Keep documentation updated**: Always update README and docs when adding features
2. **Maintain a changelog**: Document changes between versions
3. **Use git tags**: Tag releases in your repository with version numbers
4. **Test thoroughly**: Run tests before publishing new versions
5. **Respond to issues**: Monitor and respond to issues reported by users
