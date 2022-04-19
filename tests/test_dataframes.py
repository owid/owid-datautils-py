"""Test functions in scripts.dataframes module.

"""

import numpy as np
import pandas as pd

from owid.datautils import dataframes


class TestCompareDataFrames:
    def test_with_large_absolute_tolerance_all_equal(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2]}),
            df2=pd.DataFrame({"col_01": [2, 3]}),
            absolute_tolerance=1,
            relative_tolerance=1e-8,
        ).equals(pd.DataFrame({"col_01": [True, True]}))

    def test_with_large_absolute_tolerance_all_unequal(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2]}),
            df2=pd.DataFrame({"col_01": [2, 3]}),
            absolute_tolerance=0.9,
            relative_tolerance=1e-8,
        ).equals(pd.DataFrame({"col_01": [False, False]}))

    def test_with_large_absolute_tolerance_mixed(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2]}),
            df2=pd.DataFrame({"col_01": [2, 3.1]}),
            absolute_tolerance=1,
            relative_tolerance=1e-8,
        ).equals(pd.DataFrame({"col_01": [True, False]}))

    def test_with_large_relative_tolerance_all_equal(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2]}),
            df2=pd.DataFrame({"col_01": [2, 3]}),
            absolute_tolerance=1e-8,
            relative_tolerance=0.5,
        ).equals(pd.DataFrame({"col_01": [True, True]}))

    def test_with_large_relative_tolerance_all_unequal(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2]}),
            df2=pd.DataFrame({"col_01": [2, 3]}),
            absolute_tolerance=1e-8,
            relative_tolerance=0.3,
        ).equals(pd.DataFrame({"col_01": [False, False]}))

    def test_with_large_relative_tolerance_mixed(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2]}),
            df2=pd.DataFrame({"col_01": [2, 3]}),
            absolute_tolerance=1e-8,
            relative_tolerance=0.4,
        ).equals(pd.DataFrame({"col_01": [False, True]}))

    def test_with_dataframes_of_equal_values_but_different_indexes(self):
        # Even if dataframes are not identical, compare_dataframes should return all Trues (since it does not care about
        # indexes, only values).
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [1, 2], "col_02": ["a", "b"]}).set_index(
                "col_02"
            ),
            df2=pd.DataFrame({"col_01": [1, 2], "col_02": ["a", "c"]}).set_index(
                "col_02"
            ),
        ).equals(pd.DataFrame({"col_01": [True, True]}))

    def test_with_two_dataframes_with_object_columns_with_nans(self):
        assert dataframes.compare_dataframes(
            df1=pd.DataFrame({"col_01": [np.nan, "b", "c"]}),
            df2=pd.DataFrame({"col_01": [np.nan, "b", "c"]}),
        ).equals(pd.DataFrame({"col_01": [True, True, True]}))


class TestAreDataFramesEqual:
    def test_on_equal_dataframes_with_one_integer_column(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2, 3]}),
            df2=pd.DataFrame({"col_01": [1, 2, 3]}),
        )[0]

    def test_on_almost_equal_dataframes_but_differing_by_one_element(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2, 3]}),
            df2=pd.DataFrame({"col_01": [1, 2, 0]}),
        )[0]

    def test_on_almost_equal_dataframes_but_differing_by_type(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2, 3]}),
            df2=pd.DataFrame({"col_01": [1, 2, 3.0]}),
        )[0]

    def test_on_equal_dataframes_containing_nans(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2, np.nan]}),
            df2=pd.DataFrame({"col_01": [1, 2, np.nan]}),
        )[0]

    def test_on_equal_dataframes_containing_only_nans(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [np.nan, np.nan]}),
            df2=pd.DataFrame({"col_01": [np.nan, np.nan]}),
        )[0]

    def test_on_equal_dataframes_both_empty(self):
        assert dataframes.are_dataframes_equal(df1=pd.DataFrame(), df2=pd.DataFrame())[
            0
        ]

    def test_on_equal_dataframes_with_various_types_of_columns(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame(
                {
                    "col_01": [1, 2],
                    "col_02": [0.1, 0.2],
                    "col_03": ["1", "2"],
                    "col_04": [True, False],
                }
            ),
            df2=pd.DataFrame(
                {
                    "col_01": [1, 2],
                    "col_02": [0.1, 0.2],
                    "col_03": ["1", "2"],
                    "col_04": [True, False],
                }
            ),
        )[0]

    def test_on_almost_equal_dataframes_but_columns_sorted_differently(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame(
                {
                    "col_01": [1, 2],
                    "col_02": [0.1, 0.2],
                    "col_03": ["1", "2"],
                    "col_04": [True, False],
                }
            ),
            df2=pd.DataFrame(
                {
                    "col_02": [0.1, 0.2],
                    "col_01": [1, 2],
                    "col_03": ["1", "2"],
                    "col_04": [True, False],
                }
            ),
        )[0]

    def test_on_unequal_dataframes_with_all_columns_different(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2], "col_02": [0.1, 0.2]}),
            df2=pd.DataFrame({"col_03": [0.1, 0.2], "col_04": [1, 2]}),
        )[0]

    def test_on_unequal_dataframes_with_some_common_columns(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2], "col_02": [0.1, 0.2]}),
            df2=pd.DataFrame({"col_01": [1, 2], "col_03": [1, 2]}),
        )[0]

    def test_on_equal_dataframes_given_large_absolute_tolerance(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [10, 20]}),
            df2=pd.DataFrame({"col_01": [11, 21]}),
            absolute_tolerance=1,
            relative_tolerance=1e-8,
        )[0]

    def test_on_unequal_dataframes_given_large_absolute_tolerance(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [10, 20]}),
            df2=pd.DataFrame({"col_01": [11, 21]}),
            absolute_tolerance=0.9,
            relative_tolerance=1e-8,
        )[0]

    def test_on_equal_dataframes_given_large_relative_tolerance(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1]}),
            df2=pd.DataFrame({"col_01": [2]}),
            absolute_tolerance=1e-8,
            relative_tolerance=0.5,
        )[0]

    def test_on_unequal_dataframes_given_large_relative_tolerance(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1]}),
            df2=pd.DataFrame({"col_01": [2]}),
            absolute_tolerance=1e-8,
            relative_tolerance=0.49,
        )[0]

    def test_on_equal_dataframes_with_non_numeric_indexes(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2], "col_02": ["a", "b"]}).set_index(
                "col_02"
            ),
            df2=pd.DataFrame({"col_01": [1, 2], "col_02": ["a", "b"]}).set_index(
                "col_02"
            ),
        )[0]

    def test_on_dataframes_of_equal_values_but_different_indexes(self):
        assert not dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [1, 2], "col_02": ["a", "b"]}).set_index(
                "col_02"
            ),
            df2=pd.DataFrame({"col_01": [1, 2], "col_02": ["a", "c"]}).set_index(
                "col_02"
            ),
        )[0]

    def test_on_dataframes_with_object_columns_with_nans(self):
        assert dataframes.are_dataframes_equal(
            df1=pd.DataFrame({"col_01": [np.nan, "b", "c"]}),
            df2=pd.DataFrame({"col_01": [np.nan, "b", "c"]}),
        )[0]


class TestGroupbyAggregate:
    def test_default_aggregate_single_groupby_column_as_string(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2003, 2003, 2003, 2002, 2002],
                "value_01": [1, 2, 3, 4, 5, 6],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [1, 11, 9],
            }
        ).set_index("year")
        assert dataframes.groupby_agg(
            df_in,
            "year",
            aggregations=None,
            num_allowed_nans=None,
            frac_allowed_nans=None,
        ).equals(df_out)

    def test_default_aggregate_single_groupby_column_as_list(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2003, 2003, 2003, 2002, 2002],
                "value_01": [1, 2, 3, 4, 5, 6],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [1, 11, 9],
            }
        ).set_index("year")
        assert dataframes.groupby_agg(
            df_in,
            ["year"],
            aggregations=None,
            num_allowed_nans=None,
            frac_allowed_nans=None,
        ).equals(df_out)

    def test_default_aggregate_with_some_nans_ignored(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [0.0, 2.0, 15.0],
            }
        ).set_index("year")
        assert dataframes.groupby_agg(
            df_in,
            ["year"],
            aggregations=None,
            num_allowed_nans=None,
            frac_allowed_nans=None,
        ).equals(df_out)

    def test_default_aggregate_with_some_nans_ignored_different_types(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": ["a", "b", "c", "d", "e", "f"],
                "value_03": [True, False, False, True, True, False],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [0.0, 2.0, 15.0],
                "value_02": ["a", "bc", "def"],
                "value_03": [1, 0, 2],
            }
        ).set_index("year")
        assert dataframes.groupby_agg(
            df_in,
            ["year"],
            aggregations=None,
            num_allowed_nans=None,
            frac_allowed_nans=None,
        ).equals(df_out)

    def test_default_aggregate_with_some_nans_ignored_different_types_and_more_nans(
        self,
    ):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, True, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [0.0, 2.0, 15.0],
                "value_02": [0, "b", "def"],
                "value_03": [0, 0, 2],
            }
        ).set_index("year")
        df_out["value_03"] = df_out["value_03"].astype(object)
        assert dataframes.groupby_agg(
            df_in,
            ["year"],
            aggregations=None,
            num_allowed_nans=None,
            frac_allowed_nans=None,
        ).equals(df_out)

    def test_default_aggregate_with_num_allowed_nans_zero(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, True, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [np.nan, np.nan, 15.0],
                "value_02": [np.nan, np.nan, "def"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [np.nan, 0, np.nan], index=[2001, 2002, 2003], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=0,
                frac_allowed_nans=None,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_num_allowed_nans_one(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, np.nan, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [0.0, 2.0, 15.0],
                "value_02": [0, "b", "def"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [0, 0, np.nan], index=[2001, 2002, 2003], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=1,
                frac_allowed_nans=None,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_num_allowed_nans_two(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, np.nan, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [0.0, 2.0, 15.0],
                "value_02": [0, "b", "def"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [0, 0, 1], index=[2001, 2002, 2003], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=2,
                frac_allowed_nans=None,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_num_allowed_nans_the_length_of_the_dataframe(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2004, 2004, 2004, 2004],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6, 7],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f", "g"],
                "value_03": [np.nan, False, False, True, np.nan, np.nan, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2004],
                "value_01": [0.0, 2.0, 22.0],
                "value_02": [0, "b", "defg"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [0, 0, 1], index=[2001, 2002, 2004], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=None,
                frac_allowed_nans=len(df_in),
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_frac_allowed_nans_zero(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, True, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [np.nan, np.nan, 15.0],
                "value_02": [np.nan, np.nan, "def"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [np.nan, 0, np.nan], index=[2001, 2002, 2003], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=None,
                frac_allowed_nans=0,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_frac_allowed_nans_half(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, np.nan, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [np.nan, 2.0, 15.0],
                "value_02": [np.nan, "b", "def"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [np.nan, 0, np.nan], index=[2001, 2002, 2003], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=None,
                frac_allowed_nans=0.5,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_frac_allowed_nans_two_thirds(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f"],
                "value_03": [np.nan, False, False, True, np.nan, np.nan],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [np.nan, 2.0, 15.0],
                "value_02": [np.nan, "b", "def"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [np.nan, 0, 1], index=[2001, 2002, 2003], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=None,
                frac_allowed_nans=0.67,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_frac_allowed_nans_one(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003, 2004, 2004, 2004, 2004],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6, 7, np.nan, np.nan, np.nan],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f", "g", "h", "i", "j"],
                "value_03": [
                    np.nan,
                    False,
                    False,
                    True,
                    np.nan,
                    np.nan,
                    np.nan,
                    np.nan,
                    np.nan,
                    True,
                ],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003, 2004],
                "value_01": [0, 2.0, 15.0, 7],
                "value_02": [0, "b", "def", "ghij"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [0, 0, 1, 1], index=[2001, 2002, 2003, 2004], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=None,
                frac_allowed_nans=None,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_both_num_allowed_nans_and_frac_allowed_nans(self):
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003, 2004, 2004, 2004, 2004],
                "value_01": [np.nan, 2, np.nan, 4, 5, 6, 7, np.nan, np.nan, np.nan],
                "value_02": [np.nan, "b", np.nan, "d", "e", "f", "g", "h", "i", "j"],
                "value_03": [
                    np.nan,
                    False,
                    False,
                    True,
                    np.nan,
                    np.nan,
                    np.nan,
                    np.nan,
                    np.nan,
                    True,
                ],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003, 2004],
                "value_01": [np.nan, 2.0, 15.0, np.nan],
                "value_02": [np.nan, "b", "def", "ghij"],
            }
        ).set_index("year")
        df_out["value_03"] = pd.Series(
            [np.nan, 0, np.nan, np.nan], index=[2001, 2002, 2003, 2004], dtype=object
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=None,
                num_allowed_nans=2,
                frac_allowed_nans=0.5,
            ),
            df2=df_out,
        )[0]

    def test_default_aggregate_with_two_groupby_columns(self):
        df_in = pd.DataFrame(
            {
                "country": [
                    "country_a",
                    "country_a",
                    "country_a",
                    "country_b",
                    "country_b",
                    "country_c",
                ],
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [1, 2, 3, 4, 5, 6],
            }
        )
        df_out = pd.DataFrame(
            {
                "country": ["country_a", "country_a", "country_b", "country_c"],
                "year": [2001, 2002, 2003, 2003],
                "value_01": [1, 5, 9, 6],
            }
        ).set_index(["country", "year"])
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["country", "year"],
                aggregations=None,
                num_allowed_nans=None,
                frac_allowed_nans=None,
            ),
            df2=df_out,
        )[0]

    def test_custom_aggregate(self):
        aggregations = {"value_01": "sum", "value_02": "mean"}
        df_in = pd.DataFrame(
            {
                "year": [2001, 2002, 2002, 2003, 2003, 2003],
                "value_01": [1, 2, 3, 4, 5, np.nan],
                "value_02": [1, 2, 3, 4, 5, 6],
            }
        )
        df_out = pd.DataFrame(
            {
                "year": [2001, 2002, 2003],
                "value_01": [1.0, 5.0, np.nan],
                "value_02": [1, 2.5, 7.5],
            }
        ).set_index("year")
        assert dataframes.are_dataframes_equal(
            df1=dataframes.groupby_agg(
                df_in,
                ["year"],
                aggregations=aggregations,
                num_allowed_nans=0,
                frac_allowed_nans=None,
            ),
            df2=df_out,
        )


class TestMultiMerge:
    df1 = pd.DataFrame({"col_01": ["aa", "ab", "ac"], "col_02": ["ba", "bb", "bc"]})

    def test_merge_identical_dataframes(self):
        df1 = self.df1.copy()
        df2 = self.df1.copy()
        df3 = self.df1.copy()
        assert dataframes.multi_merge(
            [df1, df2, df3], how="inner", on=["col_01", "col_02"]
        ).equals(df1)

    def test_inner_join_with_non_overlapping_dataframes(self):
        df1 = self.df1.copy()
        df2 = pd.DataFrame({"col_01": ["ad", "ae"]})
        df3 = pd.DataFrame({"col_01": ["af"], "col_03": ["ca"]})
        # For some reason the order of columns changes on the second merge.
        df_out = pd.DataFrame({"col_02": [], "col_01": [], "col_03": []}, dtype=str)
        assert dataframes.are_dataframes_equal(
            df1=dataframes.multi_merge([df1, df2, df3], how="inner", on="col_01"),
            df2=df_out,
        )

    def test_outer_join_with_non_overlapping_dataframes(self):
        df1 = self.df1.copy()
        df2 = pd.DataFrame({"col_01": ["ad"]})
        df3 = pd.DataFrame({"col_01": ["ae"]})
        df_out = pd.DataFrame(
            {
                "col_01": ["aa", "ab", "ac", "ad", "ae"],
                "col_02": ["ba", "bb", "bc", np.nan, np.nan],
            }
        )
        assert dataframes.are_dataframes_equal(
            df1=dataframes.multi_merge([df1, df2, df3], how="outer", on="col_01"),
            df2=df_out,
        )[0]

    def test_left_join(self):
        df1 = self.df1.copy()
        df2 = pd.DataFrame(
            {
                "col_01": ["aa", "ab", "ad"],
                "col_02": ["ba", "bB", "bc"],
                "col_03": [1, 2, 3],
            }
        )
        # df_12 = pd.DataFrame({'col_01': ['aa', 'ab', 'ac'], 'col_02': ['ba', 'bb', 'bc'],
        #                       'col_03': [1, np.nan, np.nan]})
        df3 = pd.DataFrame({"col_01": [], "col_02": [], "col_04": []})
        df_out = pd.DataFrame(
            {
                "col_01": ["aa", "ab", "ac"],
                "col_02": ["ba", "bb", "bc"],
                "col_03": [1, np.nan, np.nan],
                "col_04": [np.nan, np.nan, np.nan],
            }
        )
        assert dataframes.multi_merge(
            [df1, df2, df3], how="left", on=["col_01", "col_02"]
        ).equals(df_out)

    def test_right_join(self):
        df1 = self.df1.copy()
        df2 = pd.DataFrame(
            {
                "col_01": ["aa", "ab", "ad"],
                "col_02": ["ba", "bB", "bc"],
                "col_03": [1, 2, 3],
            }
        )
        # df12 = pd.DataFrame({'col_01': ['aa', 'ab', 'ad'], 'col_02': ['ba', 'bB', 'bc'], 'col_03': [1, 2, 3]})
        df3 = pd.DataFrame(
            {"col_01": ["aa", "ae"], "col_02": ["ba", "be"], "col_04": [4, 5]}
        )
        df_out = pd.DataFrame(
            {
                "col_01": ["aa", "ae"],
                "col_02": ["ba", "be"],
                "col_03": [1, np.nan],
                "col_04": [4, 5],
            }
        )
        assert dataframes.multi_merge(
            [df1, df2, df3], how="right", on=["col_01", "col_02"]
        ).equals(df_out)
