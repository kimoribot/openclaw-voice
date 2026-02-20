"""
OpenClaw Voice - Discord Voice Bot Package
"""
__version__ = "1.0.0"

from .config import (
    BOT_TOKEN, BOT_NAME, DEFAULT_VOLUME, NOTIFIER_PORT,
    VERBOSITY, ENABLE_AI, OLLAMA_URL, should_respond
)

__all__ = [
    'BOT_TOKEN', 'BOT_NAME', 'DEFAULT_VOLUME', 'NOTIFIER_PORT',
    'VERBOSITY', 'ENABLE_AI', 'OLLAMA_URL', 'should_respond'
]
