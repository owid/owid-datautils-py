"""Input/Output functions for local files."""

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Hashable, List, Tuple, Union

from owid.datautils.common import warn_on_list_of_entities
from owid.datautils.web import download_file_from_url


def _load_json_data_and_duplicated_keys(
    ordered_pairs: List[Tuple[Hashable, Any]]
) -> Any:
    clean_dict = {}
    duplicated_keys = []
    for key, value in ordered_pairs:
        if key in clean_dict:
            duplicated_keys.append(key)
        clean_dict[key] = value
    if len(duplicated_keys) > 0:
        warn_on_list_of_entities(
            list_of_entities=duplicated_keys,
            warning_message="Duplicated entities found.",
            show_list=True,
        )

    return clean_dict


def load_json(json_file: Union[str, Path], warn_on_duplicated_keys: bool = True) -> Any:
    """Load data from json file, and optionally warn if there are duplicated keys.

    If json file contains duplicated keys, a warning is optionally raised, and only the value of the latest duplicated
    key is kept.

    Parameters
    ----------
    json_file : Path or str
        Path to json file.
    warn_on_duplicated_keys : bool
        True to raise a warning if there are duplicated keys in json file. False to ignore.

    Returns
    -------
    data : dict
        Data loaded from json file.

    """
    with open(json_file, "r") as _json_file:
        json_content = _json_file.read()
        if warn_on_duplicated_keys:
            data = json.loads(
                json_content, object_pairs_hook=_load_json_data_and_duplicated_keys
            )
        else:
            data = json.loads(json_content)

    return data


def save_json(data: Any, json_file: Union[str, Path], **kwargs: Any) -> None:
    """Save data to a json file.

    Parameters
    ----------
    data : list
        Data to be stored in a json file.
    json_file : str
        Path to output json file.
    kwargs:
        Additional keyword arguments for json.dump (e.g. indent=4, sort_keys=True).

    """
    # Ensure json_file is a path.
    json_file = Path(json_file)

    # Ensure output directory exists.
    json_file.parent.mkdir(parents=True, exist_ok=True)

    with open(json_file, "w") as _json_file:
        json.dump(data, _json_file, **kwargs)


def decompress_file(
    input_file: Union[str, Path],
    output_folder: Union[str, Path],
    overwrite: bool = False,
    **kwargs: Any
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
    if str(input_file).startswith("http"):
        # If input path is a URL, first download the zipped file into a temporary folder.
        with tempfile.NamedTemporaryFile() as temp_file:
            download_file_from_url(str(input_file), temp_file.name, **kwargs)
            # Open the zipped file.
            zip_file = zipfile.ZipFile(temp_file.name)
    else:
        # Directly open the local zipped file.
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
