import logging
import os
from typing import Iterable, List

import requests

LOGGER = logging.getLogger(__name__)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")


def _call_ollama_embeddings(inputs: List[str]) -> List[List[float]]:
    embeddings: List[List[float]] = []
    for text in inputs:
        payload = {
            "model": OLLAMA_EMBED_MODEL,
            "prompt": text or "",
        }
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        data = response.json()
        vector = data.get("embedding")
        if not vector:
            raise RuntimeError("Unexpected Ollama embeddings response format")
        embeddings.append(vector)
    return embeddings


def embed_text(text: str) -> List[float]:
    return _call_ollama_embeddings([text or ""])[0]


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    inputs = [t or "" for t in texts]
    return _call_ollama_embeddings(inputs)
