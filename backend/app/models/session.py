"""
Session manager — holds in-memory data sessions with full undo/redo history.
Each session stores a stack of DataFrame snapshots keyed by a session_id.
"""

import uuid
import copy
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd


class HistoryEntry:
    """A single entry in the undo/redo history."""

    def __init__(self, operation: str, description: str, dataframe: pd.DataFrame,
                 rows_affected: int, columns_affected: list[str]):
        self.operation = operation
        self.description = description
        self.dataframe = dataframe.copy()
        self.rows_affected = rows_affected
        self.columns_affected = columns_affected
        self.timestamp = datetime.now(timezone.utc).isoformat()


class DataSession:
    """Represents a single user's data session with full history."""

    def __init__(self, session_id: str, original_df: pd.DataFrame, filename: str):
        self.session_id = session_id
        self.filename = filename
        self.original_df = original_df.copy()

        # History stack: index 0 = original, subsequent = after each operation
        self.history: list[HistoryEntry] = [
            HistoryEntry(
                operation="upload",
                description=f"Loaded {filename} ({original_df.shape[0]} rows × {original_df.shape[1]} columns)",
                dataframe=original_df,
                rows_affected=0,
                columns_affected=[]
            )
        ]
        self.current_index: int = 0
        self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def df(self) -> pd.DataFrame:
        """Get the current state of the DataFrame."""
        return self.history[self.current_index].dataframe.copy()

    def push_state(self, operation: str, description: str, new_df: pd.DataFrame,
                   rows_affected: int, columns_affected: list[str]) -> int:
        """Add a new state after a cleaning operation. Truncates any redo history."""
        # Remove any states after current (truncate redo stack)
        self.history = self.history[:self.current_index + 1]

        entry = HistoryEntry(
            operation=operation,
            description=description,
            dataframe=new_df,
            rows_affected=rows_affected,
            columns_affected=columns_affected
        )
        self.history.append(entry)
        self.current_index += 1
        return self.current_index

    def undo(self) -> Optional[pd.DataFrame]:
        """Go back one step. Returns the restored DataFrame or None if can't undo."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.df
        return None

    def redo(self) -> Optional[pd.DataFrame]:
        """Go forward one step. Returns the restored DataFrame or None if can't redo."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.df
        return None

    def jump_to(self, index: int) -> Optional[pd.DataFrame]:
        """Jump to a specific history index."""
        if 0 <= index < len(self.history):
            self.current_index = index
            return self.df
        return None

    @property
    def can_undo(self) -> bool:
        return self.current_index > 0

    @property
    def can_redo(self) -> bool:
        return self.current_index < len(self.history) - 1

    def get_history(self) -> list[dict[str, Any]]:
        """Get full history as a list of dicts."""
        return [
            {
                "index": i,
                "operation": entry.operation,
                "description": entry.description,
                "rows_affected": entry.rows_affected,
                "columns_affected": entry.columns_affected,
                "timestamp": entry.timestamp,
                "is_current": i == self.current_index,
            }
            for i, entry in enumerate(self.history)
        ]


class SessionManager:
    """Global session store. In production, consider Redis or database-backed storage."""

    def __init__(self):
        self._sessions: dict[str, DataSession] = {}

    def create_session(self, df: pd.DataFrame, filename: str) -> DataSession:
        """Create a new data session and return it."""
        session_id = str(uuid.uuid4())
        session = DataSession(session_id, df, filename)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[DataSession]:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all active sessions."""
        return [
            {
                "session_id": s.session_id,
                "filename": s.filename,
                "rows": s.df.shape[0],
                "columns": s.df.shape[1],
                "created_at": s.created_at,
                "history_length": len(s.history),
            }
            for s in self._sessions.values()
        ]


# Global singleton
session_manager = SessionManager()
