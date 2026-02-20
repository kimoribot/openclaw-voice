"""
OpenClaw Voice - Config
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

def should_respond(level='minimal'):
    """Check if we should respond based on verbosity"""
    levels = ['silent', 'minimal', 'normal', 'verbose']
    try:
        current = levels.index(VERBOSITY)
        required = levels.index(level)
        return current >= required
    except ValueError:
        return True
