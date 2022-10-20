"""Test functions in owid.datautils.io.local module.

"""
from owid.datautils.io.df import from_file
from typing import Any
import pandas as pd
from pytest import raises


class TestLoadDf:
    df_original = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["a", "b", "c"])

    def test_from_file_basic(self, tmpdir):
        output_methods = {
            "csv": self.df_original.to_csv,
            # "dta": self.df_original.to_stata,
            "feather": self.df_original.to_feather,
            "parquet": self.df_original.to_parquet,
            "pickle": self.df_original.to_pickle,
            "pkl": self.df_original.to_pickle,
            "xlsx": self.df_original.to_excel,
            "xml": self.df_original.to_xml,
        }
        for extension, funct in output_methods.items():
            file = tmpdir / f"test.{extension}"
            if extension in ["dta", "pickle", "pkl", "feather"]:
                funct(file)
            else:
                funct(file, index=False)
            df = from_file(str(file))
            assert df.equals(self.df_original)

    def test_from_file_json(self, tmpdir):
        file = tmpdir / "test.json"
        self.df_original.to_json(file, orient="records")
        df = from_file(str(file))
        assert df.equals(self.df_original)
        # Compressed
        file = tmpdir / "test.zip"
        self.df_original.to_json(file, orient="records")
        df = from_file(str(file), file_type="json")
        assert df.equals(self.df_original)

    def test_from_file_html(self, tmpdir):
        file = tmpdir / "test.html"
        self.df_original.to_html(file, index=False)
        df = from_file(str(file))[0]
        assert df.equals(self.df_original)

    def test_from_file_hdf(self, tmpdir):  # hdf5?
        file = tmpdir / "test.hdf"
        self.df_original.to_hdf(file, key="df")
        df = from_file(str(file))
        assert df.equals(self.df_original)

    def test_from_file_dta(self, tmpdir):
        file = tmpdir / "test.dta"
        self.df_original.to_stata(file, write_index=False)
        df = from_file(str(file))
        assert df.astype(int).equals(self.df_original.astype(int))
        # Compressed
        file = tmpdir / "test.zip"
        self.df_original.to_stata(file, write_index=False)
        df = from_file(str(file), file_type="dta")
        assert df.astype(int).equals(self.df_original.astype(int))

    def test_from_file_csv_zip(self, tmpdir):
        file = tmpdir / "test.zip"
        self.df_original.to_csv(file, index=False)
        df = from_file(str(file), file_type="csv")
        assert df.equals(self.df_original)

    def test_from_file_filenotfound(self, tmpdir):
        """File does not exist."""
        with raises(FileNotFoundError):
            file = tmpdir / "test.csv"
            _ = from_file(str(file))

    def test_from_file_zip_err(self, tmpdir):
        """Compressed file, but no file type is given."""
        with raises(ValueError):
            file = tmpdir / "test.zip"
            _ = from_file(str(file))

    def test_from_file_format_err(self, tmpdir):
        """Unknown file format."""
        with raises(ValueError):
            file = tmpdir / "test.error"
            _create_csv_file(file)
            _ = from_file(str(file))


def _create_csv_file(file: Any) -> Any:
    content = "a,b,c\n1,2,3\n4,5,6"
    file.write_text(content, encoding="utf-8")
