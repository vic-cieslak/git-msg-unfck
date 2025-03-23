#!/usr/bin/env python3

import os
import json
import requests
from typing import Dict, Any, Optional


class OpenRouterClient:
    """Client for the OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenRouter client."""
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/yourusername/git-msg-unfck",  # Update with your actual repo
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get a list of available models from OpenRouter."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting available models: {e}")
            return {"data": []}
    
    def generate_message(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Optional[str]:
        """Generate a message using the specified model."""
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a senior software engineer with expertise in writing clear, concise, and informative Git commit messages."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            
            return None
        
        except requests.RequestException as e:
            print(f"Error generating message: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response: {e.response.text}")
            return None


def create_prompt(
    diff: str,
    original_message: str,
    reason: Optional[str] = None,
) -> str:
    """Create a prompt for the LLM to generate a new commit message."""
    prompt = """You are a senior software engineer. Rewrite the following Git commit message based on the diff and context.

Commit Diff:
```
{diff}
```

Original Message:
"{original_message}"
""".format(diff=diff, original_message=original_message)
    
    if reason:
        prompt += f"""
Additional Context:
The developer indicated the goal of this commit was to "{reason}".
"""
    
    prompt += """
Respond only with the improved commit message. Follow these guidelines:
1. Be concise but descriptive
2. Start with a verb in the present tense (e.g., "Add", "Fix", "Update")
3. Explain what changed and why, if apparent from the diff
4. Keep it under 72 characters for the first line
5. You may add a more detailed explanation after a blank line if necessary
"""
    
    return prompt


def get_improved_message(
    diff: str,
    original_message: str,
    reason: Optional[str] = None,
    model: str = "gpt-4",
    api_key: Optional[str] = None,
) -> Optional[str]:
    """Get an improved commit message from the LLM."""
    try:
        client = OpenRouterClient(api_key)
        prompt = create_prompt(diff, original_message, reason)
        return client.generate_message(prompt, model)
    
    except Exception as e:
        print(f"Error getting improved message: {e}")
        return None
