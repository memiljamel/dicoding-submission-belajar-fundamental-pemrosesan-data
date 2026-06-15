import unittest
from unittest.mock import patch, MagicMock

import pandas as pd

from utils.load import store_to_csv, store_to_postgresql


class TestStoreToCsv(unittest.TestCase):
    def test_store_to_csv_calls_to_csv(self):
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

        filename = 'products.csv'

        with patch.object(df, 'to_csv') as mock_to_csv, patch('builtins.print') as mock_print:
            store_to_csv(df, filename)

            mock_to_csv.assert_called_once_with(filename, index=False)
            mock_print.assert_called_once_with("Data berhasil disimpan ke products.csv")


class TestStoreToPostgresql(unittest.TestCase):
    @patch('utils.load.create_engine')
    def test_store_to_postgresql_success(self, mock_create_engine):
        df = pd.DataFrame({'col1': [1], 'col2': [2]})

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine

        db_url = 'postgresql+psycopg2://postgres:@localhost:5432/test'

        with patch.object(df, 'to_sql') as mock_to_sql, patch('builtins.print') as mock_print:
            store_to_postgresql(df, db_url)

            mock_create_engine.assert_called_once_with(db_url)
            mock_to_sql.assert_called_once_with(
                'productstoscrape', con=mock_conn, if_exists='append', index=False
            )
            mock_print.assert_called_once_with("Data berhasil disimpan ke database")

    @patch('utils.load.create_engine')
    def test_store_to_postgresql_failure(self, mock_create_engine):
        df = pd.DataFrame({'col1': [1]})
        mock_create_engine.side_effect = Exception("Connection error")

        db_url = 'postgresql+psycopg2://postgres:@localhost:5432/test'

        with patch('builtins.print') as mock_print:
            store_to_postgresql(df, db_url)

            printed_args = [c.args[0] for c in mock_print.call_args_list]
            self.assertTrue(
                any("Terjadi kesalahan saat menyimpan data" in msg for msg in printed_args)
            )


if __name__ == '__main__':
    unittest.main()
