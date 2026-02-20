"""
OpenClaw Voice - Discord Voice Bot Package

A flexible Discord voice channel bot - plays streams, TTS notifications.
The "brain" is in OpenClaw, this is just the renderer.
"""
__version__ = "1.1.0"

from .config import (
    BOT_TOKEN, BOT_NAME, DEFAULT_VOLUME, NOTIFIER_PORT,
    VERBOSITY, should_respond
)

__all__ = [
    'BOT_TOKEN', 'BOT_NAME', 'DEFAULT_VOLUME', 'NOTIFIER_PORT',
    'VERBOSITY', 'should_respond', 'run'
]
