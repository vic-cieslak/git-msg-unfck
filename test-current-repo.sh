#!/bin/bash

# Script to test git-msg-unfck on the current repository

# Check if OpenRouter API key is provided
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable must be set"
    echo "Usage: OPENROUTER_API_KEY=your_key ./test-current-repo.sh"
    exit 1
fi

# Install the package in development mode if not already installed
if ! command -v unfck &> /dev/null; then
    echo "Installing git-msg-unfck in development mode..."
    pip install -e .
fi

# Get the last commit hash
LAST_COMMIT=$(git rev-parse HEAD)
echo "Last commit: $LAST_COMMIT"

# Get the original commit message
ORIGINAL_MSG=$(git log -1 --pretty=%B)
echo "Original message: '$ORIGINAL_MSG'"

# Run unfck on the last commit
echo -e "\nRunning git-msg-unfck on the last commit..."
./unfck.py last 1 --just-fix-it --model anthropic/claude-3-7-sonnet-20240229

# Get the new commit message
NEW_MSG=$(git log -1 --pretty=%B)
echo -e "\nNew message: '$NEW_MSG'"

# Compare the messages
if [ "$ORIGINAL_MSG" != "$NEW_MSG" ]; then
    echo -e "\n✅ Success! The commit message was improved."
else
    echo -e "\n❌ Error: The commit message was not changed."
fi
