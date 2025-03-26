"""This module contains tests for the setup_db module."""

from unittest.mock import patch, MagicMock, call
from setup.setup_db import get_db


@patch("setup.setup_db.sqlite3.connect")
def test_get_db_creates_tables(mock_connect):
    """Test if get_db creates the required tables."""
    # Mock the connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Call the function
    year = 2023
    conn = get_db(year)

    # Verify the database name
    mock_connect.assert_called_once_with(f"expenses_{year}.db")

    # Debug: Print actual calls to mock_cursor.execute
    print(mock_cursor.execute.call_args_list)

    # Verify the SQL commands to create tables
    expected_calls = [
        call(
            """CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        category TEXT,
                        item TEXT,
                        location TEXT,
                        price REAL,
                        currency TEXT,
                        price_sgd REAL)"""
        ),
        call(
            """CREATE TABLE IF NOT EXISTS recurring_expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_date TEXT,
                        end_date TEXT,
                        category TEXT,
                        item TEXT,
                        location TEXT,
                        ori_price REAL,
                        currency TEXT,
                        price_sgd REAL)"""
        ),
        call(
            """CREATE TABLE IF NOT EXISTS salary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_date TEXT,
                        end_date TEXT,
                        amount REAL)"""
        ),
    ]
    print()
    print(expected_calls)
    mock_cursor.execute.assert_has_calls(expected_calls, any_order=True)

    # Verify commit is called
    mock_conn.commit.assert_called_once()

    # Verify the function returns the connection object
    assert conn == mock_conn
