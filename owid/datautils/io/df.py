"""DataFrame io operations."""
import pandas as pd
from pathlib import Path
from owid.datautils.decorators import enable_file_download
from typing import Any, Optional, Union, List


COMPRESSION_SUPPORTED = ["gz", "bz2", "zip", "xz", "zst", "tar"]


@enable_file_download("file_path")
def from_file(
    file_path: Union[str, Path], file_type: Optional[str] = None, **kwargs: Any
) -> Union[pd.DataFrame, List[pd.DataFrame]]:
    """Loads a file as a pandas DataFrame.

    It uses standard pandas function pandas.read_* but adds the ability to read from a URL in some
    cases where pandas does not work.

    The function will infer the extension of `file_path` by simply taking what follows the last ".". For example:
    "file.csv" will be read as a csv file, and "http://my/domain/file.xlsx" will be read as an excel file.

    Reading from compressed files will not work by default, unless you provide a `file_type`.

    Parameters
    ----------
    filepath : str
        Path or url to file.
    file_type : str
        File type of the data file. By default is None, as it is only required when reading compressed files.
        This is typically equivalent to the file extension. However, when reading a
        compressed file, this refers to the actual file that is compressed (not the compressed file extension).
        Reading from compressed files is supported for "csv", "dta" and "json".
    kwargs :
        pandas.read_* arguments.

    Returns
    -------
    pandas.DataFrame:
        Read dataframe.
    """
    # Ensure file_path is a Path object.
    file_path = Path(file_path)

    # Ensure extension is lower case and does not start with '.'.
    extension = file_path.suffix.lstrip(".").lower()

    # If compressed file, raise an exception unless file_type is given
    if extension in COMPRESSION_SUPPORTED:
        if file_type:
            extension = file_type
        else:
            raise ValueError(
                "To be able to read from a compressed file, you need to provide a value"
                " for `file_type`."
            )

    # Check path is valid
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot find file: {file_path}")

    # Available input methods (some of them may need additional dependencies to work).
    input_methods = {
        "csv": pd.read_csv,
        "dta": pd.read_stata,
        "feather": pd.read_feather,
        "hdf": pd.read_hdf,
        "html": pd.read_html,
        "json": pd.read_json,
        "parquet": pd.read_parquet,
        "pickle": pd.read_pickle,
        "pkl": pd.read_pickle,
        "xlsx": pd.read_excel,
        "xml": pd.read_xml,
    }
    if extension not in output_methods:
        raise ValueError(
            "Failed reading dataframe because of an unknown file extension:"
            f" {extension}"
        )
    # Select the appropriate reading method.
    read_function = input_methods[extension]

    # Load file using the chosen read function and the appropriate arguments.
    df: pd.DataFrame = read_function(file_path, **kwargs)
    return df
