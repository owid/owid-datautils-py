"""Input/Output functions for local files."""

import zipfile
from pathlib import Path
from typing import Union

from owid.datautils.decorators import enable_url_download


@enable_url_download(path_arg_name="input_file")
def decompress_file(
    input_file: Union[str, Path],
    output_folder: Union[str, Path],
    overwrite: bool = False,
) -> None:
    """Extract a local zip file, or a remote zip file given its URL.

    Parameters
    ----------
    input_file : Union[str, Path]
        Path to local zip file, or URL of a remote zip file.
    output_folder : Union[str, Path]
        Path to local folder
    overwrite : bool
        Overwrite decompressed content if it already exists (otherwise raise an error).

    """
    zip_file = zipfile.ZipFile(input_file)

    # If the content to be written in output folder already exists, raise an error,
    # unless 'overwrite' is set to True, in which case the existing file will be overwritten.
    # Path to new file to be created.
    new_file = Path(output_folder) / Path(zip_file.namelist()[0])
    if new_file.exists() and not overwrite:
        raise FileExistsError(
            "Output already exists. Either change output_folder or use overwrite=True."
        )

    # Unzip the file and save it in the local output folder.
    # Note that, if output_folder path does not exist, the following command will create it.
    zip_file.extractall(output_folder)
