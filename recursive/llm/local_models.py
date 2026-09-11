#!/usr/bin/env python3

import os
from pathlib import Path


DEFAULT_OLLAMA_MODELS_DIR = Path.home() / ".ollama" / "models"


def get_ollama_models_dir():
    """Return the Ollama models directory from env or the standard user path."""
    configured = os.getenv("OLLAMA_MODELS_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_OLLAMA_MODELS_DIR


def list_ollama_models(models_dir=None):
    """
    Discover installed Ollama model manifests and return WriteHERE model ids.

    Ollama stores manifests below:
      ~/.ollama/models/manifests/<registry>/<namespace>/<model>/<tag>

    WriteHERE exposes those as:
      ollama/<model>:<tag>
      ollama/<namespace>/<model>:<tag> when the namespace is not "library"
    """
    base_dir = Path(models_dir).expanduser() if models_dir else get_ollama_models_dir()
    manifests_dir = base_dir / "manifests"
    if not manifests_dir.exists() or not manifests_dir.is_dir():
        return []

    models = set()
    for manifest in manifests_dir.rglob("*"):
        if not manifest.is_file():
            continue

        rel_parts = manifest.relative_to(manifests_dir).parts
        if len(rel_parts) < 4:
            continue

        namespace = rel_parts[-3]
        model_name = rel_parts[-2]
        tag = rel_parts[-1]

        if namespace == "library":
            ollama_name = f"{model_name}:{tag}"
        else:
            ollama_name = f"{namespace}/{model_name}:{tag}"
        models.add(f"ollama/{ollama_name}")

    return sorted(models)


def build_model_options():
    """Return frontend-ready metadata for discovered local Ollama models."""
    return [
        {
            "label": f"Local Ollama - {model[len('ollama/'):] if model.startswith('ollama/') else model}",
            "value": model,
            "provider": "ollama",
            "local": True,
        }
        for model in list_ollama_models()
    ]
