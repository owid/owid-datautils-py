"""Test functions in owid.datautils.io.local module.

"""
from owid.datautils.io.df import read_csv, read_excel
from typing import Any
import pandas as pd


class TestLoadDf:
    df_original = pd.DataFrame([[1, 2, 3]], columns=["a", "b", "c"])

    def test_read_csv(self, tmpdir):
        file = tmpdir / "test.csv"
        _create_csv_file(file)
        df = read_csv(str(file))
        assert df.equals(self.df_original)

    def test_read_excel(self, tmpdir):
        file = tmpdir / "test.xlsx"
        _create_excel_file(file)
        df = read_excel(str(file))
        assert df.equals(self.df_original)


def _create_csv_file(file: Any) -> Any:
    content = "a,b,c\n1,2,3"
    file.write_text(content, encoding="utf-8")


def _create_excel_file(file: Any) -> Any:
    df = pd.DataFrame([[1, 2, 3]], columns=["a", "b", "c"])
    df.to_excel(file, index=False)
