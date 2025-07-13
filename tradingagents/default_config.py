import os
from pathlib import Path

# Load .env file with graceful fallback
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    load_dotenv(dotenv_path=env_file)
except ImportError:
    # dotenv not available - environment variables can still be passed directly
    pass


def get_env_var(key: str, default: str = "") -> str:
    """Get environment variable with default fallback."""
    return os.getenv(key, default)


def get_custom_config() -> dict:
    """Generate custom configuration from environment variables."""
    custom_api_url = get_env_var("CUSTOM_API_URL")
    if not custom_api_url:
        return {}
    
    custom_api_key = get_env_var("CUSTOM_API_KEY", "dummy-key")
    custom_model_name = get_env_var("CUSTOM_MODEL_NAME", "gemini-2.5-pro")
    
    return {
        "llm_provider": "openai",  # Use OpenAI-compatible provider
        "backend_url": custom_api_url,
        "custom_api_key": custom_api_key,
        "deep_think_llm": custom_model_name,
        "quick_think_llm": custom_model_name,
    }


DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
}

# Merge custom configuration from environment variables
custom_config = get_custom_config()
DEFAULT_CONFIG.update(custom_config)
