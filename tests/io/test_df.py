"""Test functions in owid.datautils.io.local module.

"""
from owid.datautils.io.df import read_csv
from typing import Any
import pandas as pd


class TestLoadDf:
    def test_read_csv(self, tmpdir):
        file = tmpdir / "test.csv"
        _create_csv_file(file)
        df = read_csv(str(file))
        df_ = pd.DataFrame([[1, 2, 3]], columns=["a", "b", "c"])
        assert df.equals(df_)


def _create_csv_file(file: Any) -> Any:
    content = "a,b,c\n1,2,3"
    file.write_text(content, encoding="utf-8")
