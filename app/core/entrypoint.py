from __future__ import annotations

import os
import subprocess
import time


def run_migrations_with_retry(retries: int = 20, wait_seconds: float = 2.0) -> None:
    """Run alembic migrations, retrying while DB container becomes ready."""
    last_err: Exception | None = None
    for _ in range(retries):
        try:
            subprocess.check_call(["alembic", "upgrade", "head"])
            return
        except Exception as e:  # noqa: BLE001 (fine for bootstrap)
            last_err = e
            time.sleep(wait_seconds)
    raise RuntimeError("alembic upgrade head failed after retries") from last_err


def main() -> int:
    if os.getenv("RUN_MIGRATIONS", "1") == "1":
        run_migrations_with_retry()

    port = os.getenv("PORT", "8000")
    # Nota: "app.main:app" asume que tu FastAPI app está ahí.
    subprocess.check_call(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())