"""
StudyMate AI — Database Module.

Manages SQLite database connection, schema creation, and provides
async database access utilities using aiosqlite.
"""

import aiosqlite
from pathlib import Path
from typing import Any, Optional

from backend.config import get_settings
from utils.logger import get_logger

logger = get_logger("database")

# ── Schema Definition ─────────────────────────────────────────────────────

SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    difficulty_level TEXT DEFAULT 'medium',
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Topics table
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority INTEGER DEFAULT 3,
    status TEXT DEFAULT 'not_started',
    created_at TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Study Sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    subject_id TEXT,
    topic_id TEXT,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    notes TEXT DEFAULT '',
    started_at TEXT NOT NULL,
    ended_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- Progress table
CREATE TABLE IF NOT EXISTS progress (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    confidence_score REAL DEFAULT 0.0,
    revision_count INTEGER DEFAULT 0,
    last_reviewed TEXT,
    next_review TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Quiz Scores table
CREATE TABLE IF NOT EXISTS quiz_scores (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic_id TEXT,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    score_percentage REAL NOT NULL,
    quiz_data TEXT DEFAULT '{}',
    taken_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- Revision History table
CREATE TABLE IF NOT EXISTS revision_history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    revision_type TEXT DEFAULT 'review',
    notes TEXT DEFAULT '',
    revised_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Preferences table
CREATE TABLE IF NOT EXISTS preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    study_hours_per_day REAL DEFAULT 4.0,
    preferred_session_length INTEGER DEFAULT 45,
    difficulty_preference TEXT DEFAULT 'medium',
    learning_style TEXT DEFAULT 'visual',
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Memory table (conversation memory)
CREATE TABLE IF NOT EXISTS memory (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Agent Logs table
CREATE TABLE IF NOT EXISTS agent_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    step_type TEXT NOT NULL,
    content TEXT DEFAULT '',
    tool_name TEXT,
    tool_input TEXT,
    tool_output TEXT,
    step_number INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_subjects_user ON subjects(user_id);
CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_user ON progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_topic ON progress(topic_id);
CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_user_conv ON memory(user_id, conversation_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_user_conv ON agent_logs(user_id, conversation_id);
"""


class Database:
    """Async SQLite database manager."""

    def __init__(self) -> None:
        self._db_path: str = ""
        self._initialized: bool = False

    async def initialize(self) -> None:
        """Initialize the database with the schema."""
        settings = get_settings()
        self._db_path = settings.database_url

        # Ensure the data directory exists
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self._db_path) as db:
            await db.executescript(SCHEMA_SQL)
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA foreign_keys=ON")
            await db.commit()

        self._initialized = True
        logger.info("Database initialized at %s", self._db_path)

    async def execute(
        self, query: str, params: tuple = ()
    ) -> Optional[list[dict[str, Any]]]:
        """
        Execute a query and return results as a list of dicts.

        Args:
            query: SQL query string with ? placeholders.
            params: Query parameters tuple.

        Returns:
            List of row dicts for SELECT queries, None for others.
        """
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            cursor = await db.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                await db.commit()
                return None

    async def execute_one(
        self, query: str, params: tuple = ()
    ) -> Optional[dict[str, Any]]:
        """
        Execute a query and return the first result row.

        Args:
            query: SQL query string.
            params: Query parameters tuple.

        Returns:
            First row as dict, or None if no results.
        """
        results = await self.execute(query, params)
        if results and len(results) > 0:
            return results[0]
        return None

    async def execute_many(
        self, query: str, params_list: list[tuple]
    ) -> None:
        """
        Execute a query for multiple parameter sets.

        Args:
            query: SQL query string.
            params_list: List of parameter tuples.
        """
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys=ON")
            await db.executemany(query, params_list)
            await db.commit()

    async def execute_scalar(
        self, query: str, params: tuple = ()
    ) -> Any:
        """
        Execute a query and return a single scalar value.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            Single value from the first column of the first row.
        """
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(query, params)
            row = await cursor.fetchone()
            return row[0] if row else None


# Global database instance
db = Database()
