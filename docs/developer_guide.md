# StudyMate AI — Developer Guide

## Architecture Principles

- **Clean Architecture**: Layers don't reach across boundaries
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **No Hardcoded Workflows**: The LLM decides which tools to call
- **Type Hints Everywhere**: Full typing for IDE support and documentation
- **Async by Default**: All I/O operations are async

## Adding a New MCP Tool

1. Create `mcp_server/tools/your_tool.py`:

```python
import json

def register_tools(mcp) -> None:
    @mcp.tool()
    def your_tool_name(param1: str, param2: int = 5) -> str:
        """Tool description for the LLM."""
        result = {"success": True, "data": "..."}
        return json.dumps(result, indent=2)
```

2. Register it in `mcp_server/server.py`:

```python
from mcp_server.tools.your_tool import register_tools as reg_your_tool
reg_your_tool(mcp)
```

That's it — the agent will automatically discover and use the new tool.

## Adding a New API Endpoint

1. Create or update the Pydantic model in `backend/models/`
2. Add business logic in `backend/services/`
3. Create the router in `backend/routers/`
4. Register it in `backend/main.py`

## Key Design Patterns

- **Singleton Services**: Database, LLM client, MCP client are singletons
- **Repository Pattern**: Services encapsulate all database access
- **Decorator Pattern**: Retry logic applied via decorators
- **Context Variables**: Correlation IDs propagated via contextvars
- **Strategy Pattern**: Primary/fallback LLM model selection

## Testing

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_tools/test_study_planner.py -v

# With coverage
python -m pytest tests/ --cov=backend --cov=agent -v
```
