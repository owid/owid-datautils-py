"""Test functions in owid.datautils.io.local module.

"""

from pytest import warns
from unittest.mock import patch, mock_open

from owid.datautils.io.local import load_json


class TestLoadJson:

    @patch("builtins.open", new_callable=mock_open, read_data='{"1": "10", "2": "20"}')
    def test_load_json_without_duplicated_keys(self, _):
        assert load_json(_) == {"1": "10", "2": "20"}

    @patch("builtins.open", new_callable=mock_open, read_data='{"1": "10", "2": "20", "1": "100"}')
    def test_load_json_with_duplicated_keys(self, _):
        assert load_json(_, warn_on_duplicated_keys=False) == {"1": "100", "2": "20"}

    @patch("builtins.open", new_callable=mock_open, read_data='{"1": "10", "2": "20", "1": "100"}')
    def test_warn_on_load_json_with_duplicated_keys(self, _):
        with warns(UserWarning, match="Duplicated"):
            load_json(_, warn_on_duplicated_keys=True)

    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    def test_load_empty_json(self, _):
        assert load_json(_) == {}
