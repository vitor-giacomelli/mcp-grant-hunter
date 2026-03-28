import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any


class OAuthSessionStore:
    """Simple SQLite-backed store for OAuth session credentials."""

    def __init__(self, db_path: Optional[str] = None):
        default_path = Path(".agent/staging/data/oauth_sessions.db")
        configured = Path(db_path) if db_path else default_path
        configured.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(configured)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS oauth_sessions (
                    session_id TEXT PRIMARY KEY,
                    label TEXT,
                    oauth_token TEXT NOT NULL,
                    refresh_token TEXT,
                    client_id TEXT,
                    client_secret TEXT,
                    token_uri TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create_session(
        self,
        oauth_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        token_uri: str,
        label: Optional[str] = None,
    ) -> Dict[str, Any]:
        session_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO oauth_sessions (
                    session_id, label, oauth_token, refresh_token, client_id,
                    client_secret, token_uri, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    label,
                    oauth_token,
                    refresh_token,
                    client_id,
                    client_secret,
                    token_uri,
                    now,
                    now,
                ),
            )
            conn.commit()
        return {"session_id": session_id, "created_at": now, "label": label}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT session_id, label, oauth_token, refresh_token,
                       client_id, client_secret, token_uri, created_at, updated_at
                FROM oauth_sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        if not row:
            return None
        return dict(row)

    def update_access_token(self, session_id: str, oauth_token: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            result = conn.execute(
                """
                UPDATE oauth_sessions
                SET oauth_token = ?, updated_at = ?
                WHERE session_id = ?
                """,
                (oauth_token, now, session_id),
            )
            conn.commit()
            return result.rowcount > 0

    def delete_session(self, session_id: str) -> bool:
        with self._connect() as conn:
            result = conn.execute(
                "DELETE FROM oauth_sessions WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()
            return result.rowcount > 0
