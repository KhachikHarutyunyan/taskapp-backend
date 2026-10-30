import os
from pathlib import Path

from dotenv import dotenv_values

_ROOT = Path(__file__).resolve().parents[1]


def _apply_file(path: Path) -> None:
    if not path.is_file():
        return
    for key, value in dotenv_values(path).items():
        if value:
            os.environ.setdefault(key, value)


def ensure_test_env() -> None:
    """Fill missing settings before the app is imported.

    Already exported variables stay in place. A local .env is applied next.
    Committed test defaults cover keys that are still empty, which is the CI case.
    """
    _apply_file(_ROOT / ".env")
    _apply_file(_ROOT / "tests" / ".env.test")


ensure_test_env()
