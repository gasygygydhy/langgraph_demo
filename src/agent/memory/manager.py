from contextlib import contextmanager
from typing import Optional, Tuple, Any
from agent.env_utils import DB_URI
from langgraph.checkpoint.memory import InMemorySaver


@contextmanager
def memory_context() -> Tuple[Optional[Any], Any]:
    store = None
    checkpointer = None
    if DB_URI:
        try:
            from langgraph.store.postgres import PostgresStore
            from langgraph.checkpoint.postgres import PostgresSaver
            with (
                PostgresStore.from_conn_string(DB_URI) as s,
                PostgresSaver.from_conn_string(DB_URI) as c,
            ):
                s.setup()
                yield s, c
                return
        except Exception:
            pass
    checkpointer = InMemorySaver()
    yield store, checkpointer

