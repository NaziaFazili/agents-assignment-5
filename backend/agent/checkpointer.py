"""
Checkpointer factory for the Financial Approval workflow.

Provides SQLite-based persistence so that interrupted workflows
can be resumed after human review decisions.
"""

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from backend.config import CHECKPOINT_DB


def create_checkpointer() -> SqliteSaver:
    """
    Create a SQLite checkpointer for workflow persistence.

    The checkpointer stores graph state at each node transition,
    enabling the interrupt/resume pattern for human-in-the-loop.

    Use this one in synchronous scripts and tests (graph.invoke / graph.stream).
    SqliteSaver does not implement the async API, so the server uses
    create_async_checkpointer() instead.

    Returns:
        SqliteSaver: Configured SQLite checkpointer instance
    """
    conn = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
    return SqliteSaver(conn)


def create_async_checkpointer():
    """
    Async context manager yielding an AsyncSqliteSaver on the same database.

    The AG-UI endpoint drives the graph through its async API (aget_state,
    astream_events), which SqliteSaver rejects with NotImplementedError.
    AsyncSqliteSaver must be created inside a running event loop.

    Usage:
        async with create_async_checkpointer() as checkpointer:
            graph = create_approval_graph(checkpointer=checkpointer)
    """
    return AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB)
