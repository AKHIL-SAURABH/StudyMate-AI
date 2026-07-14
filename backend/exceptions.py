"""
StudyMate AI — Custom Exceptions.

Defines a hierarchy of application-specific exceptions
for clean error handling across all layers.
"""


class StudyMateError(Exception):
    """Base exception for all StudyMate AI errors."""

    def __init__(self, message: str = "An unexpected error occurred", code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


# ── Authentication Errors ──────────────────────────────────────────────

class AuthenticationError(StudyMateError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, code="AUTH_ERROR")


class UserNotFoundError(StudyMateError):
    """Raised when a requested user does not exist."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"User not found: {identifier}" if identifier else "User not found"
        super().__init__(message=msg, code="USER_NOT_FOUND")


class UserAlreadyExistsError(StudyMateError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"User already exists: {identifier}" if identifier else "User already exists"
        super().__init__(message=msg, code="USER_EXISTS")


# ── Resource Errors ────────────────────────────────────────────────────

class ResourceNotFoundError(StudyMateError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource_type: str = "Resource", resource_id: str = "") -> None:
        msg = f"{resource_type} not found: {resource_id}" if resource_id else f"{resource_type} not found"
        super().__init__(message=msg, code="NOT_FOUND")


class ValidationError(StudyMateError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message=message, code="VALIDATION_ERROR")


# ── Agent Errors ───────────────────────────────────────────────────────

class AgentError(StudyMateError):
    """Base exception for agent-related errors."""

    def __init__(self, message: str = "Agent error occurred") -> None:
        super().__init__(message=message, code="AGENT_ERROR")


class LLMError(AgentError):
    """Raised when the LLM API call fails."""

    def __init__(self, message: str = "LLM API call failed") -> None:
        super().__init__(message=message)
        self.code = "LLM_ERROR"


class ToolExecutionError(AgentError):
    """Raised when an MCP tool execution fails."""

    def __init__(self, tool_name: str = "", message: str = "Tool execution failed") -> None:
        self.tool_name = tool_name
        full_msg = f"Tool '{tool_name}' failed: {message}" if tool_name else message
        super().__init__(message=full_msg)
        self.code = "TOOL_ERROR"


class MaxIterationsError(AgentError):
    """Raised when the ReAct loop exceeds maximum iterations."""

    def __init__(self, max_iterations: int = 5) -> None:
        super().__init__(
            message=f"Agent exceeded maximum iterations ({max_iterations})"
        )
        self.code = "MAX_ITERATIONS"


class JSONParseError(AgentError):
    """Raised when LLM output cannot be parsed as valid JSON."""

    def __init__(self, raw_output: str = "") -> None:
        self.raw_output = raw_output
        super().__init__(message="Failed to parse LLM output as JSON")
        self.code = "JSON_PARSE_ERROR"


# ── MCP Errors ─────────────────────────────────────────────────────────

class MCPConnectionError(StudyMateError):
    """Raised when the MCP client cannot connect to the server."""

    def __init__(self, message: str = "Failed to connect to MCP server") -> None:
        super().__init__(message=message, code="MCP_CONNECTION_ERROR")


class MCPToolNotFoundError(StudyMateError):
    """Raised when a requested MCP tool does not exist."""

    def __init__(self, tool_name: str = "") -> None:
        msg = f"MCP tool not found: {tool_name}" if tool_name else "MCP tool not found"
        super().__init__(message=msg, code="MCP_TOOL_NOT_FOUND")


# ── Database Errors ────────────────────────────────────────────────────

class DatabaseError(StudyMateError):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message=message, code="DATABASE_ERROR")
