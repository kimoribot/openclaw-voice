"""
OpenClaw Voice - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
BOT_NAME = os.getenv('BOT_NAME', 'OpenClaw')
DEFAULT_VOLUME = float(os.getenv('DEFAULT_VOLUME', '0.8'))
NOTIFIER_PORT = int(os.getenv('NOTIFIER_PORT', '5000'))

# Verbosity levels: silent, minimal, normal, verbose
VERBOSITY = os.getenv('VERBOSITY', 'minimal')  # default to minimal

# Feature flags
ENABLE_AI = os.getenv('ENABLE_AI', 'true').lower() == 'true'
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
# Alternative: use a dedicated OpenClaw endpoint
OPENCLAW_URL = os.getenv('OPENCLAW_URL', OLLAMA_URL)

def should_respond(level='minimal'):
    """Check if we should respond based on verbosity setting"""
    levels = ['silent', 'minimal', 'normal', 'verbose']
    try:
        current = levels.index(VERBOSITY)
        required = levels.index(level)
        return current >= required
    except ValueError:
        return True
