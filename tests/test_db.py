"""Tests for src/db.py"""


def test_db_url_is_set():
    from src.db import DB_URL
    assert DB_URL.startswith("postgresql://")


def test_pool_size_default():
    from src.db import POOL_SIZE
    assert POOL_SIZE > 0
