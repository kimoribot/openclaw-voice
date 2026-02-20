"""
OpenClaw Discord Voice - Config
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
BOT_NAME = os.getenv('BOT_NAME', 'OpenClaw')
DEFAULT_VOLUME = float(os.getenv('DEFAULT_VOLUME', '0.8'))
NOTIFIER_PORT = int(os.getenv('NOTIFIER_PORT', '5000'))

# Verbosity: silent, minimal, normal, verbose
VERBOSITY = os.getenv('VERBOSITY', 'minimal')

# Text channel response when speaking in voice
# Options: always, never, errors_only
TEXT_RESPONSE = os.getenv('TEXT_RESPONSE', 'always')

def should_respond_in_text():
    """Check if we should respond in text channel when speaking"""
    if TEXT_RESPONSE == 'always':
        return True
    elif TEXT_RESPONSE == 'never':
        return False
    elif TEXT_RESPONSE == 'errors_only':
        return False  # Only errors would be handled separately
    return True

def should_respond(level='minimal'):
    """Check if we should respond based on verbosity"""
    levels = ['silent', 'minimal', 'normal', 'verbose']
    try:
        current = levels.index(VERBOSITY)
        required = levels.index(level)
        return current >= required
    except ValueError:
        return True