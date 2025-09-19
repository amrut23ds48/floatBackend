import os
from dotenv import load_dotenv

# Load env file
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")

# Chroma Cloud config
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")

# Perplexity config
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
