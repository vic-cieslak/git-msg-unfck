# Publishing to PyPI

This document outlines the steps to build and publish the `git-msg-unfck` package to PyPI.

## Prerequisites

1. You need a PyPI account. If you don't have one, register at https://pypi.org/account/register/
2. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Configure Poetry with your PyPI credentials:
   ```bash
   poetry config pypi-token.pypi your-api-token
   ```
   You can generate an API token in your PyPI account settings.

## Building the Package

1. Make sure your `pyproject.toml` file is up to date with the correct version number.
2. Build the package:
   ```bash
   poetry build
   ```
   This will create distribution files in the `dist/` directory.

## Testing the Package Locally

Before publishing to PyPI, it's a good idea to test the package locally:

1. Create a virtual environment:
   ```bash
   python -m venv test-env
   source test-env/bin/activate  # On Windows: test-env\Scripts\activate
   ```

2. Install the package from the local distribution:
   ```bash
   pip install dist/git_msg_unfck-x.y.z-py3-none-any.whl
   ```
   (Replace x.y.z with the actual version number)

3. Test that the package works as expected:
   ```bash
   unfck --help
   ```

## Publishing to PyPI

Once you've tested the package and everything works as expected, you can publish it to PyPI:

```bash
poetry publish
```

Or if you want to build and publish in one step:

```bash
poetry publish --build
```

## Publishing to TestPyPI (Optional)

If you want to test the publishing process without affecting the real PyPI, you can use TestPyPI:

1. Configure Poetry to use TestPyPI:
   ```bash
   poetry config repositories.testpypi https://test.pypi.org/legacy/
   poetry config pypi-token.testpypi your-test-pypi-token
   ```

2. Publish to TestPyPI:
   ```bash
   poetry publish -r testpypi
   ```

3. Install from TestPyPI to verify:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ git-msg-unfck
   ```

## Updating the Package

When you need to publish a new version:

1. Update the version in `pyproject.toml`:
   ```toml
   [tool.poetry]
   name = "git-msg-unfck"
   version = "x.y.z"  # Update this
   ```

2. Build and publish as described above.

## Automating with GitHub Actions (Optional)

You can automate the publishing process using GitHub Actions. Create a workflow file at `.github/workflows/publish.yml`:

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
