"""Objects related to pandas dataframes.

"""

import numpy as np
import pandas as pd
from typing import Tuple, Union, List, Any, Dict

from owid.datautils.common import ExceptionFromDocstring


class DataFramesHaveDifferentLengths(ExceptionFromDocstring):
    """Dataframes cannot be compared because they have different number of rows."""


class ObjectsAreNotDataframes(ExceptionFromDocstring):
    """Given objects are not dataframes."""


def compare(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    columns: Union[List[str], None] = None,
    absolute_tolerance: Union[int, float] = 1e-8,
    relative_tolerance: Union[int, float] = 1e-8,
) -> pd.DataFrame:
    """Compare two dataframes element by element, assuming that nans are all identical, and assuming certain absolute
    and relative tolerances for the comparison of floats.

    NOTE: Dataframes must have the same number of rows to be able to compare them.

    Parameters
    ----------
    df1 : pd.DataFrame
        First dataframe.
    df2 : pd.DataFrame
        Second dataframe.
    columns : list or None
        List of columns to compare (they both must exist in both dataframes). If None, common columns will be compared.
    absolute_tolerance : float
        Absolute tolerance to assume in the comparison of each cell in the dataframes. A value a of an element in df1 is
        considered equal to the corresponding element b at the same position in df2, if:
        abs(a - b) <= absolute_tolerance
    relative_tolerance : float
        Relative tolerance to assume in the comparison of each cell in the dataframes. A value a of an element in df1 is
        considered equal to the corresponding element b at the same position in df2, if:
        abs(a - b) / abs(b) <= relative_tolerance

    Returns
    -------
    compared : pd.DataFrame
        Dataframe with as many rows as df1 and df2, and as many columns as specified by `columns` argument (or as many
        common columns between df1 and df2, if `columns` is None).

    """
    # Ensure dataframes can be compared.
    if (type(df1) != pd.DataFrame) or (type(df2) != pd.DataFrame):
        raise ObjectsAreNotDataframes
    if len(df1) != len(df2):
        raise DataFramesHaveDifferentLengths

    # If columns are not specified, assume common columns.
    if columns is None:
        columns = sorted(set(df1.columns) & set(df2.columns))

    # Compare, column by column, the elements of the two dataframes.
    compared = pd.DataFrame()
    for col in columns:
        if (df1[col].dtype == object) or (df2[col].dtype == object):
            # Apply a direct comparison for strings.
            compared_row = df1[col].values == df2[col].values
        else:
            # For numeric data, consider them equal within certain absolute and relative tolerances.
            compared_row = np.isclose(
                df1[col].values,
                df2[col].values,
                atol=absolute_tolerance,
                rtol=relative_tolerance,
            )
        # Treat nans as equal.
        compared_row[pd.isnull(df1[col].values) & pd.isnull(df2[col].values)] = True
        compared[col] = compared_row

    return compared


def are_equal(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    absolute_tolerance: Union[int, float] = 1e-8,
    relative_tolerance: Union[int, float] = 1e-8,
    verbose: bool = True,
) -> Tuple[bool, pd.DataFrame]:
    """Check whether two dataframes are equal, assuming that all nans are identical, and comparing floats by means of
    certain absolute and relative tolerances.

    Parameters
    ----------
    df1 : pd.DataFrame
        First dataframe.
    df2 : pd.DataFrame
        Second dataframe.
    absolute_tolerance : float
        Absolute tolerance to assume in the comparison of each cell in the dataframes. A value a of an element in df1 is
        considered equal to the corresponding element b at the same position in df2, if:
        abs(a - b) <= absolute_tolerance
    relative_tolerance : float
        Relative tolerance to assume in the comparison of each cell in the dataframes. A value a of an element in df1 is
        considered equal to the corresponding element b at the same position in df2, if:
        abs(a - b) / abs(b) <= relative_tolerance
    verbose : bool
        True to print a summary of the comparison of the two dataframes.

    Returns
    -------
    are_equal : bool
        True if the two dataframes are equal (given the conditions explained above).
    compared : pd.DataFrame
        Dataframe with the same shape as df1 and df2 (if they have the same shape) that is True on each element where
        both dataframes have equal values. If dataframes have different shapes, compared will be empty.

    """
    # Initialise flag that is True only if both dataframes are equal.
    equal = True
    # Initialise flag that is True if dataframes can be compared cell by cell.
    can_be_compared = True
    # Initialise string of messages, which will optionally be printed.
    summary = ""

    # Check if all columns in df2 are in df1.
    missing_in_df1 = sorted(set(df2.columns) - set(df1.columns))
    if len(missing_in_df1):
        summary += f"\n* {len(missing_in_df1)} columns in df2 missing in df1.\n"
        summary += "\n".join([f"  * {col}" for col in missing_in_df1])
        equal = False

    # Check if all columns in df1 are in df2.
    missing_in_df2 = sorted(set(df1.columns) - set(df2.columns))
    if len(missing_in_df2):
        summary += f"\n* {len(missing_in_df2)} columns in df1 missing in df2.\n"
        summary += "\n".join([f"  * {col}" for col in missing_in_df2])
        equal = False

    # Check if dataframes have the same number of rows.
    if len(df1) != len(df2):
        summary += f"\n* {len(df1)} rows in df1 and {len(df2)} rows in df2."
        equal = False
        can_be_compared = False

    # Check for differences in column names or types.
    common_columns = sorted(set(df1.columns) & set(df2.columns))
    all_columns = sorted(set(df1.columns) | set(df2.columns))
    if common_columns == all_columns:
        if df1.columns.tolist() != df2.columns.tolist():
            summary += "\n* Columns are sorted differently.\n"
            equal = False
        for col in common_columns:
            if df1[col].dtype != df2[col].dtype:
                summary += (
                    f"  * Column {col} is of type {df1[col].dtype} for df1, but type"
                    f" {df2[col].dtype} for df2."
                )
                equal = False
    else:
        summary += (
            f"\n* Only {len(common_columns)} common columns out of"
            f" {len(all_columns)} distinct columns."
        )
        equal = False

    if not can_be_compared:
        # Dataframes cannot be compared.
        compared = pd.DataFrame()
        equal = False
    else:
        # Check if indexes are equal.
        if (df1.index != df2.index).any():
            summary += (
                "\n* Dataframes have different indexes (consider resetting indexes of"
                " input dataframes)."
            )
            equal = False

        # Dataframes can be compared cell by cell (two nans on the same cell are considered equal).
        compared = compare(
            df1,
            df2,
            columns=common_columns,
            absolute_tolerance=absolute_tolerance,
            relative_tolerance=relative_tolerance,
        )
        all_values_equal = compared.all().all()
        if not all_values_equal:
            summary += "\n* Values differ by more than the given absolute and relative tolerances."

        # Dataframes are equal only if all previous checks have passed.
        equal = equal & all_values_equal

    if equal:
        summary += (
            "Dataframes are identical (within absolute tolerance of"
            f" {absolute_tolerance} and relative tolerance of {relative_tolerance})."
        )

    if verbose:
        # Optionally print the summary of the comparison.
        print(summary)

    return equal, compared


def groupby_agg(
    df: pd.DataFrame,
    groupby_columns: Union[List[str], str],
    aggregations: Union[Dict[str, Any], None] = None,
    num_allowed_nans: Union[int, None] = 0,
    frac_allowed_nans: Union[float, None] = None,
) -> pd.DataFrame:
    """Group dataframe by certain columns, and aggregate using a certain method, and decide how to handle nans.

    This function is similar to the usual
    > df.groupby(groupby_columns).agg(aggregations)
    However, pandas by default ignores nans in aggregations. This implies, for example, that
    > df.groupby(groupby_columns).sum()
    will treat nans as zeros, which can be misleading.

    When both num_allowed_nans and frac_allowed_nans are None, this function behaves like the default pandas behaviour
    (and nans will be treated as zeros).

    On the other hand, if num_allowed_nans is not None, then a group will be nan if the number of nans in that group is
    larger than num_allowed_nans, otherwise nans will be treated as zeros.

    Similarly, if frac_allowed_nans is not None, then a group will be nan if the fraction of nans in that group is
    larger than frac_allowed_nans, otherwise nans will be treated as zeros.

    If both num_allowed_nans and frac_allowed_nans are not None, both conditions are applied. This means that, each
    group must have a number of nans <= num_allowed_nans, and a fraction of nans <= frac_allowed_nans, otherwise that
    group will be nan.

    Note: This function won't work when using multiple aggregations for the same column (e.g. {'a': ('sum', 'mean')}).

    Parameters
    ----------
    df : pd.DataFrame
        Original dataframe.
    groupby_columns : list or str
        List of columns to group by. It can be given as a string, if it is only one column.
    aggregations : dict or None
        Aggregations to apply to each column in df. If None, 'sum' will be applied to all columns.
    num_allowed_nans : int or None
        Maximum number of nans that are allowed in a group.
    frac_allowed_nans : float or None
        Maximum fraction of nans that are allowed in a group.

    Returns
    -------
    grouped : pd.DataFrame
        Grouped dataframe after applying aggregations.

    """
    if type(groupby_columns) == str:
        groupby_columns = [groupby_columns]

    if aggregations is None:
        columns_to_aggregate = [
            column for column in df.columns if column not in groupby_columns
        ]
        aggregations = {column: "sum" for column in columns_to_aggregate}

    # Group by and aggregate.
    grouped = df.groupby(groupby_columns, dropna=False).agg(aggregations)

    if num_allowed_nans is not None:
        # Count the number of missing values in each group.
        num_nans_detected = df.groupby(groupby_columns, dropna=False).agg(
            lambda x: pd.isnull(x).sum()
        )
        # Make nan any aggregation where there were too many missing values.
        grouped = grouped[num_nans_detected <= num_allowed_nans]

    if frac_allowed_nans is not None:
        # Count the number of missing values in each group.
        num_nans_detected = df.groupby(groupby_columns, dropna=False).agg(
            lambda x: pd.isnull(x).sum()
        )
        # Count number of elements in each group (avoid using 'count' method, which ignores nans).
        num_elements = df.groupby(groupby_columns, dropna=False).size()
        # Make nan any aggregation where there were too many missing values.
        grouped = grouped[
            num_nans_detected.divide(num_elements, axis="index") <= frac_allowed_nans
        ]

    return grouped


def multi_merge(
    dfs: List[pd.DataFrame], on: Union[List[str], str], how: str = "inner"
) -> pd.DataFrame:
    """Merge multiple dataframes.

    This is a helper function when merging more than two dataframes on common columns.

    Parameters
    ----------
    dfs : list
        Dataframes to be merged.
    on : list or str
        Column or list of columns on which to merge. These columns must have the same name on all dataframes.
    how : str
        Method to use for merging (with the same options available in pd.merge).

    Returns
    -------
    merged : pd.DataFrame
        Input dataframes merged.

    """
    merged = dfs[0].copy()
    for df in dfs[1:]:
        merged = pd.merge(merged, df, how=how, on=on)

    return merged