#!/bin/bash

# Script to test git-msg-unfck on the current repository

# Check if OpenRouter API key is provided
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable must be set"
    echo "Usage: OPENROUTER_API_KEY=your_key ./test-current-repo.sh"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed"
    echo "Please install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies
echo "Installing dependencies with Poetry..."
poetry install || {
    echo "Error: Failed to install dependencies with Poetry"
    echo "Try running 'poetry install' manually to see detailed error messages"
    exit 1
}

# Get the last commit hash
LAST_COMMIT=$(git rev-parse HEAD)
echo "Last commit: $LAST_COMMIT"

# Get the original commit message
ORIGINAL_MSG=$(git log -1 --pretty=%B)
echo "Original message: '$ORIGINAL_MSG'"

# Run unfck on the last commit using Poetry
echo -e "\nRunning git-msg-unfck on the last commit..."
poetry run python unfck.py last 1 --just-fix-it --model anthropic/claude-3-7-sonnet-20240229

# Get the new commit message
NEW_MSG=$(git log -1 --pretty=%B)
echo -e "\nNew message: '$NEW_MSG'"

# Compare the messages
if [ "$ORIGINAL_MSG" != "$NEW_MSG" ]; then
    echo -e "\n✅ Success! The commit message was improved."
else
    echo -e "\n❌ Error: The commit message was not changed."
fi
