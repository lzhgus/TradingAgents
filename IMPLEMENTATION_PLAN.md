# Implementation Plan: Custom Model Support with .env Configuration

## Overview
Add .env file support and custom model configuration to TradingAgents, inspired by zen-mcp-server patterns.

## Current State Analysis

### TradingAgents Strengths
- ✅ Flexible LLM configuration system (`DEFAULT_CONFIG` in `default_config.py`)
- ✅ Multi-provider support (OpenAI, Anthropic, Google, Ollama, OpenRouter)
- ✅ Custom backend URL support via `backend_url` config
- ✅ Custom model names via `deep_think_llm` and `quick_think_llm`

### Current Limitations
- ❌ No .env file support
- ❌ Manual environment variable handling
- ❌ No standardized custom model configuration pattern
- ❌ API keys rely on LangChain's environment variable discovery

### zen-mcp-server Patterns to Adopt
- ✅ `.env` file loading with graceful fallback
- ✅ `CUSTOM_API_URL`, `CUSTOM_API_KEY`, `CUSTOM_MODEL_NAME` environment variables
- ✅ Dummy API key handling for unauthenticated endpoints (Ollama)
- ✅ Extended timeouts for local models

## Implementation Plan

### Phase 1: Add .env File Support
**Files to modify:**
- `tradingagents/default_config.py` - Add environment variable loading
- `requirements.txt` - Add python-dotenv dependency

**Changes:**
1. Add `python-dotenv` to requirements.txt
2. Load .env file at the start of `default_config.py`
3. Create environment variable helper functions

### Phase 2: Custom Model Environment Variables
**Environment Variables to Support:**
```bash
# Custom LLM Endpoint Configuration
CUSTOM_API_URL=http://localhost:8123/hf/v1
CUSTOM_API_KEY=sk-lzhgus
CUSTOM_MODEL_NAME=gemini-2.5-pro

# Override existing configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
TRADINGAGENTS_RESULTS_DIR=./custom-results
```

### Phase 3: Configuration System Enhancement
**Files to modify:**
- `tradingagents/default_config.py` - Update DEFAULT_CONFIG with env vars
- `tradingagents/graph/trading_graph.py` - Handle custom API key injection

**Logic:**
1. Check for `CUSTOM_API_URL` - if present, use custom configuration
2. Set provider to "openai" for OpenAI-compatible endpoints
3. Use custom API key or dummy key for unauthenticated endpoints
4. Apply custom model names to both `deep_think_llm` and `quick_think_llm`

### Phase 4: Backward Compatibility
**Ensure:**
- Existing configuration methods continue to work
- Direct config dict overrides still function
- No breaking changes to existing API

### Phase 5: Documentation & Testing
**Files to create/modify:**
- `.env.example` - Example environment configuration
- `CLAUDE.md` - Update with new configuration options
- `README.md` - Add custom model setup instructions

## Detailed Implementation Steps

### Step 1: Add dotenv Support
```python
# In tradingagents/default_config.py
try:
    from dotenv import load_dotenv
    import os
    from pathlib import Path
    
    # Load .env file from project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    load_dotenv(dotenv_path=env_file)
except ImportError:
    # dotenv not available - environment variables can still be passed directly
    pass
```

### Step 2: Environment Variable Helpers
```python
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
```

### Step 3: Update DEFAULT_CONFIG
```python
# Merge custom config with defaults
custom_config = get_custom_config()
DEFAULT_CONFIG.update(custom_config)

# Update results directory from environment
if results_dir := get_env_var("TRADINGAGENTS_RESULTS_DIR"):
    DEFAULT_CONFIG["results_dir"] = results_dir
```

### Step 4: LLM Initialization Enhancement
```python
# In tradingagents/graph/trading_graph.py
def create_llm_with_custom_key(config: dict, model: str):
    """Create LLM with custom API key if provided."""
    api_key = config.get("custom_api_key")
    
    if config["llm_provider"] == "openai":
        kwargs = {
            "model": model,
            "base_url": config.get("backend_url"),
            "temperature": 0.7,
        }
        if api_key:
            kwargs["api_key"] = api_key
        return ChatOpenAI(**kwargs)
    
    # Handle other providers...
```

## Example .env Configuration

```bash
# Custom LLM Configuration
CUSTOM_API_URL=http://localhost:8123/hf/v1
CUSTOM_API_KEY=sk-lzhgus
CUSTOM_MODEL_NAME=gemini-2.5-pro

# Traditional API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Application Settings
TRADINGAGENTS_RESULTS_DIR=./custom-results
```

## Testing Strategy

### Unit Tests
- Test environment variable loading
- Test configuration merging
- Test custom LLM initialization

### Integration Tests
- Test with Gemini via custom endpoint
- Test with Ollama local endpoint
- Test backward compatibility

### Manual Testing
- Create .env file with custom configuration
- Run trading agents with custom model
- Verify API calls go to custom endpoint

## Success Criteria

- ✅ .env file loads successfully with graceful fallback
- ✅ Custom API endpoints work with OpenAI-compatible format
- ✅ Gemini models work through custom endpoints
- ✅ Backward compatibility maintained
- ✅ Documentation updated
- ✅ All existing tests pass
- ✅ New functionality tested

## Rollback Plan

If issues arise:
1. All changes are additive - no existing functionality removed
2. Default behavior unchanged if no .env file present
3. Can disable custom configuration by removing CUSTOM_API_URL

## Timeline

- **Phase 1**: 30 minutes (dotenv support)
- **Phase 2**: 45 minutes (environment variables)
- **Phase 3**: 60 minutes (configuration enhancement)
- **Phase 4**: 15 minutes (compatibility verification)
- **Phase 5**: 30 minutes (documentation)

**Total Estimated Time**: 3 hours

## Dependencies

- `python-dotenv` package (add to requirements.txt)
- No breaking changes to existing dependencies