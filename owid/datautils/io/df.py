"""DataFrame io operations."""
import pandas as pd
from owid.datautils.decorators import enable_file_download
from typing import Any


@enable_file_download("path_or_url")
def read_csv(path_or_url: str, **kwargs: Any) -> pd.DataFrame:
    """Read a CSV.

    It uses standard pandas function pandas.read_csv but adds the ability to read from a URL in some cases where
    pandas.read_csv does not work.

    Parameters
    ----------
    path_or_url : str
        Path or url to file.
    kwargs : _type_
        pandas.read_csv arguments.

    Returns
    -------
    pandas.DataFrame:
        Read dataframe.
    """
    df: pd.DataFrame = pd.read_csv(path_or_url, **kwargs)
    return df


@enable_file_download("path_or_url")
def read_excel(path_or_url: str, **kwargs: Any) -> pd.DataFrame:
    """Read an excel file (xlsx or xls).

    It uses standard pandas function pandas.read_excel but adds the ability to read from a URL in some cases where
    pandas.read_excel does not work.

    Parameters
    ----------
    path_or_url : str
        Path or url to file.
    kwargs : _type_
        pandas.read_csv arguments.

    Returns
    -------
    pandas.DataFrame:
        Read dataframe.
    """
    df: pd.DataFrame = pd.read_excel(path_or_url, **kwargs)
    return df
