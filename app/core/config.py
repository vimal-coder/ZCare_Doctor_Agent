import os
import configparser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Extract the API Key securely
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY is not set in the .env file")

# Initialize the parser for config.ini
config = configparser.ConfigParser()
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_path = os.path.join(base_dir, 'config.ini')
config.read(config_path)

# Extract model configurations
MODEL_ID = config.get('MODEL', 'MODEL_ID', fallback='gemini-2.5-flash')
TEMPERATURE = config.getfloat('MODEL', 'TEMPERATURE', fallback=0.0)
MAX_TOKENS = config.getint('MODEL', 'MAX_TOKENS', fallback=8192)