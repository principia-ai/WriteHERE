#!/usr/bin/env python3
"""
LLM module for WriteHERE project.

This module provides unified interfaces for different LLM providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- OpenRouter (various models)
- Minimax (M2 models)
"""

from .llm import OpenAIApiProxy
from .minimax import MinimaxM2Client


def get_llm_client(model_name, verbose=True):
    """
    Factory function to get the appropriate LLM client based on model name.

    Args:
        model_name: Name of the model (e.g., "gpt-4o", "claude-3-sonnet", "abab6.5s-chat")
        verbose: Whether to enable verbose logging

    Returns:
        An LLM client instance (OpenAIApiProxy or MinimaxM2Client)
    """
    model_name_lower = model_name.lower()

    # Check if it's a Minimax model
    if any(prefix in model_name_lower for prefix in ["abab", "minimax", "m2"]):
        return MinimaxM2Client(verbose=verbose)

    # Default to OpenAIApiProxy for all other models
    # (it handles GPT, Claude, Gemini, OpenRouter, etc.)
    return OpenAIApiProxy(verbose=verbose)


__all__ = [
    'OpenAIApiProxy',
    'MinimaxM2Client',
    'get_llm_client',
]
