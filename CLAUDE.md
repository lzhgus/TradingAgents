# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM-powered trading system built with LangGraph. It orchestrates specialized AI agents to analyze markets, debate investment strategies, and make trading decisions with risk management.

## Development Commands

### Setup
```bash
# Install dependencies
uv pip install -r requirements.txt

# Install in development mode
uv pip install -e .
```

### Running the Application
```bash
# Interactive CLI
python -m cli.main

# Programmatic execution
python main.py
```

### Environment Variables

The project supports `.env` file configuration. Copy `.env.example` to `.env` and configure:

**Custom Model Configuration** (for OpenAI-compatible endpoints):
- `CUSTOM_API_URL` - Custom API endpoint (e.g., `http://localhost:8123/hf/v1`)
- `CUSTOM_API_KEY` - API key for custom endpoint (use `dummy-key` for Ollama)
- `CUSTOM_MODEL_NAME` - Model name (e.g., `gemini-2.5-pro`)

**Standard API Keys**:
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key
- `FINNHUB_API_KEY` - Financial data API

**Application Settings**:
- `TRADINGAGENTS_RESULTS_DIR` - Custom results directory

## Architecture

### Agent Hierarchy
The system uses specialized agents organized in teams:

1. **Analyst Team** (`tradingagents/agents/analysts/`)
   - `market_analyst.py` - Technical analysis
   - `social_media_analyst.py` - Sentiment analysis
   - `news_analyst.py` - News impact assessment
   - `fundamentals_analyst.py` - Company fundamentals

2. **Research Team** (`tradingagents/agents/researcher/`)
   - Bull researcher - Optimistic analysis
   - Bear researcher - Pessimistic analysis

3. **Trading Team** (`tradingagents/agents/trader/`)
   - Trader agent - Final decision making

4. **Risk Management** (`tradingagents/agents/risk_manager/`)
   - Risk assessment and portfolio management

### Core Components

- **Agent State Management**: Uses `AgentState`, `InvestDebateState`, and `RiskDebateState` classes
- **Memory System**: `FinancialSituationMemory` for learning from past decisions
- **Tool System**: Modular tools in `tradingagents/tools/` for data fetching
- **Graph Orchestration**: LangGraph workflows in `tradingagents/graph/`

### Configuration

Default configuration is in `tradingagents/default_config.py`. Key settings:
- LLM provider and model selection
- Debate round counts
- Tool availability (online/offline mode)
- Agent prompts and behaviors

## Code Patterns

### Creating Agents
```python
from tradingagents.agents import create_trader, create_market_analyst

# Agents are created with factory functions
trader = create_trader(llm, config)
analyst = create_market_analyst(llm, config)
```

### Agent Communication
Agents communicate through structured state objects:
```python
# State flows through the graph
state = AgentState(
    stock_data=stock_data,
    reports={},
    analyst_reports={},
    # ...
)
```

### LLM Provider Flexibility
```python
# Supports multiple providers
config = {
    "llm_type": "openai",  # or "anthropic", "google", "ollama"
    "llm_config": {
        "model": "gpt-4",
        "temperature": 0.7
    }
}
```

## Development Guidelines

### When Adding New Features

1. **New Agents**: Place in appropriate subdirectory under `tradingagents/agents/`
2. **New Tools**: Add to `tradingagents/tools/` with clear interfaces
3. **State Extensions**: Update relevant state classes in `tradingagents/data_flow/state.py`
4. **CLI Commands**: Extend the Typer app in `cli/main.py`

### Code Style

- Use type hints for function parameters and returns
- Follow existing naming conventions (snake_case for functions/variables)
- Add docstrings to new functions and classes
- Keep agent logic modular and focused on single responsibilities

### Testing Approach

Currently, the project lacks formal tests. When implementing:
- Test agents individually by mocking LLM responses
- Verify state transitions in the graph
- Test tools with mock data sources
- Use the CLI for integration testing

## Common Tasks

### Running with Custom Models

**Option 1: Using .env file (Recommended)**
```bash
# Create .env file with custom configuration
cp .env.example .env
# Edit .env to set CUSTOM_API_URL, CUSTOM_API_KEY, CUSTOM_MODEL_NAME
python -m cli.main
```

**Option 2: Using environment variables**
```bash
export CUSTOM_API_URL=http://localhost:8123/hf/v1
export CUSTOM_API_KEY=sk-lzhgus
export CUSTOM_MODEL_NAME=gemini-2.5-pro
python -m cli.main
```

**Option 3: Programmatic configuration**
```python
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config.update({
    "llm_provider": "openai",
    "backend_url": "http://localhost:8123/hf/v1",
    "custom_api_key": "sk-lzhgus",
    "deep_think_llm": "gemini-2.5-pro",
    "quick_think_llm": "gemini-2.5-pro",
})
```

### Debugging Agent Decisions
- Enable verbose logging in agent creation
- Check intermediate state in graph execution
- Review agent reports in the results directory

### Adding Data Sources
1. Create new tool in `tradingagents/tools/`
2. Add to appropriate analyst's toolkit
3. Update agent prompts if needed

## Local Ollama Embeddings

The FinancialSituationMemory system uses local Ollama embeddings for improved privacy and performance:

### Prerequisites
- Ollama running on `localhost:11434`
- Model installed: `ollama pull mxbai-embed-large:latest`

### Configuration
- **Model**: `mxbai-embed-large:latest` (1024-dimensional embeddings)
- **Endpoint**: `http://localhost:11434/v1`
- **Authentication**: None required (dummy key used)

## Important Notes

- The system is designed for research and educational purposes
- Financial decisions should not be made solely based on agent outputs
- Memory system helps agents learn but requires sufficient historical data
- Rate limits on APIs (especially social media) may affect performance
- Local embeddings provide privacy benefits and eliminate external API dependencies