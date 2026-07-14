"""
StudyMate AI — MCP Server.

Registers all educational tools using FastMCP and exposes them
via stdio transport for the MCP client to discover and invoke.
"""

import sys
import json
from pathlib import Path

# Add project root to path so tools can import app modules
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP(
    "StudyMate AI Tools",
    version="1.0.0",
)


# ── Tool Imports & Registration ────────────────────────────────────────
# Each tool module registers its tools via decorators when imported.

from mcp_server.tools.study_planner import register_tools as reg_planner
from mcp_server.tools.quiz_generator import register_tools as reg_quiz
from mcp_server.tools.resource_finder import register_tools as reg_resources
from mcp_server.tools.revision_planner import register_tools as reg_revision
from mcp_server.tools.weak_topic_analyzer import register_tools as reg_weak
from mcp_server.tools.progress_tracker import register_tools as reg_progress
from mcp_server.tools.motivation_generator import register_tools as reg_motivation
from mcp_server.tools.study_statistics import register_tools as reg_stats
from mcp_server.tools.subject_analyzer import register_tools as reg_subject
from mcp_server.tools.time_estimator import register_tools as reg_time

# Register all tools with the MCP server
reg_planner(mcp)
reg_quiz(mcp)
reg_resources(mcp)
reg_revision(mcp)
reg_weak(mcp)
reg_progress(mcp)
reg_motivation(mcp)
reg_stats(mcp)
reg_subject(mcp)
reg_time(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio")
