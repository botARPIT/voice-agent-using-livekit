# Real Estate Voice Agent

A production-grade, modular voice agent system for real estate built with LiveKit Agents SDK.

## Features

- **Modular Architecture**: Clean separation of concerns with agents, tools, models, and services
- **Property Search**: Find properties by location, price, bedrooms, and more
- **Appointment Scheduling**: Schedule property viewings with availability checking
- **Mortgage Calculator**: Estimate monthly payments and affordability
- **Market Insights**: Get local market information and neighborhood details
- **Multi-Agent Workflow**: Specialized agents for different tasks with seamless handoffs
- **Telephony Support**: Handle phone calls via SIP
- **Fully Tested**: Comprehensive test suite

## Architecture

```
real_estate_agent/
├── agents/           # Agent definitions and instructions
│   ├── greeter.py
│   ├── property_search.py
│   ├── scheduling.py
│   └── builder.py
├── tools/            # AI-exposed tools
│   ├── property_tools.py
│   ├── appointment_tools.py
│   ├── mortgage_tools.py
│   └── market_tools.py
├── models/           # Data models
│   ├── property.py
│   ├── appointment.py
│   └── lead.py
├── services/         # Business logic and repositories
│   ├── repositories.py
│   ├── mortgage.py
│   └── market_data.py
├── config/           # Configuration management
│   └── settings.py
└── tests/            # Test suite
```

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your LiveKit credentials
```

Required environment variables:
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=your-secret
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Agent

```bash
# Development mode (auto-reload)
./run.sh

# Production mode
./run.sh start

# Or directly:
python run.py dev
```

### 4. Connect a Client

```python
# In another terminal
source venv/bin/activate
python client.py
```

## Agent Capabilities

### Greeter Agent
- Routes callers to appropriate specialists
- Collects initial information
- Handles general inquiries

### Property Search Agent
- Searches properties by criteria
- Provides detailed property information
- Calculates mortgage estimates
- Shares market insights
- Describes neighborhoods

### Scheduling Agent
- Checks availability
- Books property viewings
- Confirms appointment details
- Handles cancellations

## Available Tools

| Tool | Description |
|------|-------------|
| `search_properties` | Find properties by city, price, bedrooms |
| `get_property_details` | Get full property information |
| `schedule_viewing` | Book a property viewing |
| `cancel_appointment` | Cancel an existing appointment |
| `check_availability` | See available time slots |
| `get_mortgage_estimate` | Calculate monthly payments |
| `calculate_affordability` | Determine buying power |
| `get_market_insights` | Get local market data |
| `get_neighborhood_info` | Learn about neighborhoods |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=real_estate_agent

# Run specific test file
pytest real_estate_agent/tests/test_models.py
```

## Configuration

Configuration is managed via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LIVEKIT_URL` | - | LiveKit WebSocket URL |
| `LIVEKIT_API_KEY` | - | API key |
| `LIVEKIT_API_SECRET` | - | API secret |
| `LOG_LEVEL` | INFO | Logging level |
| `STT_MODEL` | deepgram/nova-3 | Speech-to-text model |
| `LLM_MODEL` | openai/gpt-4.1-mini | LLM model |
| `TTS_MODEL` | cartesia/sonic-3 | Text-to-speech model |
| `COMPANY_NAME` | DreamHome Realty | Your company name |

## Extending the System

### Adding a New Tool

1. Create tool function in `real_estate_agent/tools/`
2. Use `@function_tool` decorator
3. Add to agent in `real_estate_agent/agents/`

Example:
```python
from livekit.agents import function_tool

@function_tool
def my_new_tool(param: str) -> str:
    """Description for the AI."""
    return f"Result: {param}"
```

### Adding a New Agent

1. Create agent class in `real_estate_agent/agents/`
2. Define instructions in `instructions.py`
3. Register in `AgentBuilder`

### Adding a New Model

1. Create model in `real_estate_agent/models/`
2. Add corresponding repository in `services/repositories.py`
3. Write tests in `real_estate_agent/tests/`

## Production Deployment

### LiveKit Cloud

```bash
# Install LiveKit CLI
curl -sSL https://get.livekit.io/cli | bash
lk cloud auth

# Deploy
lk cloud agent deploy
```

### Self-Hosted

```bash
# Build Docker image
docker build -t real-estate-agent .

# Run
docker run -e LIVEKIT_URL=... -e LIVEKIT_API_KEY=... real-estate-agent
```

## Development

```bash
# Format code
black real_estate_agent/

# Type check
mypy real_estate_agent/

# Lint
ruff check real_estate_agent/
```

## License

MIT

## Support

For issues and feature requests, please open a GitHub issue.
# voice-agent-using-livekit
