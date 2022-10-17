"""DataFrame io operations."""
import pandas as pd
from owid.datautils.decorators import enable_file_download
from typing import Any


@enable_file_download("filepath")
def read_csv(filepath: str, **kwargs: Any) -> pd.DataFrame:
    """Read a CSV.

    It uses standard pandas function pandas.read_csv but adds the ability to read from a URL in some cases where
    pandas.read_csv does not work.

    Parameters
    ----------
    filepath : str
        Path or url to file.
    kwargs :
        pandas.read_csv arguments.

    Returns
    -------
    pandas.DataFrame:
        Read dataframe.
    """
    df: pd.DataFrame = pd.read_csv(filepath, **kwargs)
    return df


@enable_file_download("filepath")
def read_excel(filepath: str, **kwargs: Any) -> pd.DataFrame:
    """Read an excel file (xlsx or xls).

    It uses standard pandas function pandas.read_excel but adds the ability to read from a URL in some cases where
    pandas.read_excel does not work.

    Parameters
    ----------
    filepath : str
        Path or url to file.
    kwargs :
        pandas.read_excel arguments.

    Returns
    -------
    pandas.DataFrame:
        Read dataframe.
    """
    df: pd.DataFrame = pd.read_excel(filepath, **kwargs)
    return df
