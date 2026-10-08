import sys
from unittest.mock import patch

sys.path.insert(0, "backend")

import db


def test_connect_uses_postgresql_configuration():
    fake_connection = object()

    with patch("db.psycopg.connect", return_value=fake_connection) as connect:
        result = db.connect()

    assert result is fake_connection
    connect.assert_called_once_with(
        host=db.POSTGRES_HOST,
        port=db.POSTGRES_PORT,
        dbname=db.POSTGRES_DB,
        user=db.POSTGRES_USER,
        password=db.POSTGRES_PASSWORD,
        options=f"-c search_path={db.POSTGRES_SCHEMA}",
    )
