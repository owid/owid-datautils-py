"""Input/Output functions for local files."""

import json
from pathlib import Path
from typing import Any, cast, Dict, Hashable, List, Tuple, Union

from owid.datautils.common import warn_on_list_of_entities


def _load_json_data_and_duplicated_keys(
    ordered_pairs: List[Tuple[Hashable, Any]]
) -> Tuple[Dict[Any, Any], List[Any]]:
    clean_dict = {}
    duplicated_keys = []
    for key, value in ordered_pairs:
        if key in clean_dict:
            duplicated_keys.append(key)
        clean_dict[key] = value

    return clean_dict, duplicated_keys


def load_json(
    json_file: Union[str, Path], warn_on_duplicated_keys: bool = True
) -> Dict[Any, Any]:
    """Load data from json file, and optionally warn if there are duplicated keys.

    If json file contains duplicated keys, a warning is optionally raised, and only the latest value of the key is kept.

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
        if warn_on_duplicated_keys:
            data, duplicated_keys = json.loads(
                _json_file.read(), object_pairs_hook=_load_json_data_and_duplicated_keys
            )
            if len(duplicated_keys) > 0:
                warn_on_list_of_entities(
                    duplicated_keys,
                    f"Duplicated entities found in {json_file}",
                    show_list=True,
                )
        else:
            data = json.loads(_json_file.read())

    return cast(Dict[Any, Any], data)
