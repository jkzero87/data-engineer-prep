"""Tests for the pure record-classification logic in load.py.

These cover the data-quality behaviors that are the actual point of the
project: a missing id must be skippable, and a missing price must still be
loadable (as a stale row). They don't touch Postgres -- run() is exercised
against a real database only via the full pipeline.
"""

from load import upsert_params


def test_missing_id_is_skipped():
    assert upsert_params({"name": "Mystery Coin", "current_price": 1.0}) is None


def test_full_record_returns_id_name_price():
    coin = {"id": "bitcoin", "name": "Bitcoin", "current_price": 65000.5}
    assert upsert_params(coin) == ("bitcoin", "Bitcoin", 65000.5)


def test_missing_price_is_still_loadable_with_none_price():
    coin = {"id": "bitcoin", "name": "Bitcoin"}
    assert upsert_params(coin) == ("bitcoin", "Bitcoin", None)


def test_missing_name_is_preserved_as_none():
    coin = {"id": "bitcoin", "current_price": 65000.5}
    assert upsert_params(coin) == ("bitcoin", None, 65000.5)
