"""Postgres access for the hosted service.

Every query runs inside `Database.tx(user_id)`. It opens one transaction and
sets `app.user_id` for that transaction only. Row-level security policies read
that setting, so a query sees only the rows of that user.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

import psycopg
from psycopg_pool import ConnectionPool

DATABASE_URL_ENV = "DATABASE_URL"

# The one user that local development runs as until sign-in exists (migration
# slice S13). `supabase/seed.sql` creates the matching row.
DEV_USER_ID = UUID("00000000-0000-4000-8000-000000000001")

# The hosted demo has one owner for each deployment. When this is set, the
# service runs as that user in place of DEV_USER_ID.
WORKSPACE_USER_ID_ENV = "WORKSPACE_USER_ID"


class Database:
    def __init__(self, url: str, *, max_size: int = 10) -> None:
        self._pool = ConnectionPool(url, min_size=1, max_size=max_size, open=True)

    @contextmanager
    def tx(self, user_id: UUID | str) -> Iterator[psycopg.Connection]:
        """One transaction that acts as `user_id`.

        Commits when the block ends. Rolls back when the block raises.
        """
        # YOUR TURN (block 1, piece 1): the one door to the database.
        #
        # 1. `user_id` can be a UUID or text. Make sure you hold a UUID. Text
        #    that is not a UUID must raise ValueError, before any connection
        #    is opened. `UUID(text)` does that.
        # 2. Take one connection from `self._pool` in a `with` block. The pool
        #    commits when the block ends and rolls back when it raises.
        # 3. On that connection, run this SQL with the user id as text:
        #        select set_config('app.user_id', %s, true)
        #    The `true` means "for this transaction only".
        # 4. `yield` the connection to the caller.
        uid = user_id
        if isinstance(user_id,UUID):
            uid = user_id
        else:
            uid = UUID(user_id)
                
        with self._pool.connection() as conn:
            conn.execute("select set_config('app.user_id', %s, true)", (str(uid),))
            yield conn


        
    def close(self) -> None:
        self._pool.close()


# --- Phase 1 seam -----------------------------------------------------------
# A store still takes the state directory that it took with SQLite, and asks
# `resolve()` which database and which user that directory means. The service
# answers "the one database, the development user". Tests and evals answer "a
# new user for each directory", so two directories stay two isolated stores.
# Slice S15 removes this: each request then names its user.

Binding = tuple[Database, UUID]

_resolver: Callable[[Path], Binding] | None = None
_default: Database | None = None
_default_lock = threading.Lock()


def resolve(base_dir: str | Path) -> Binding:
    """The database and the user for a store that was opened at `base_dir`."""
    if _resolver is not None:
        return _resolver(Path(base_dir))
    return _default_database(), _service_user()


def _service_user() -> UUID:
    # YOUR TURN (block 1, piece 1): who owns the rows of this deployment.
    #
    # Read the environment variable named by WORKSPACE_USER_ID_ENV and strip
    # the spaces. When it has a value, return it as a UUID. When it is empty
    # or not set, return DEV_USER_ID.
    value = os.environ.get(WORKSPACE_USER_ID_ENV, "").strip()
    if value:
        return UUID(value)
    return DEV_USER_ID


def set_resolver(resolver: Callable[[Path], Binding] | None) -> None:
    global _resolver
    _resolver = resolver


def close_default() -> None:
    """Close the service pool, so an early exit leaves no pool thread behind."""
    global _default
    with _default_lock:
        if _default is not None:
            _default.close()
            _default = None


def _default_database() -> Database:
    global _default
    with _default_lock:
        if _default is None:
            url = os.environ.get(DATABASE_URL_ENV, "").strip()
            if not url:
                raise RuntimeError(
                    f"{DATABASE_URL_ENV} is not set. For local development, run "
                    "`make db-up` and start the backend with `make backend`."
                )
            _default = Database(url)
        return _default
