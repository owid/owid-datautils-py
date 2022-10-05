"""Test functions in owid.datautils.web module.

"""

from pytest import warns

from owid.datautils.web import get_base_url


class TestGetBaseUrl:
    def test_on_correct_urls_returning_scheme(self):
        # With http.
        assert get_base_url("http://example.com") == "http://example.com"
        assert get_base_url("http://example.com/some/path") == "http://example.com"
        assert (
            get_base_url("http://example.com.au/some/path") == "http://example.com.au"
        )
        # With https.
        assert get_base_url("https://example.com") == "https://example.com"
        assert get_base_url("https://example.com/some/path") == "https://example.com"
        assert (
            get_base_url("https://example.com.au/some/path") == "https://example.com.au"
        )

    def test_on_correct_urls_without_returning_scheme(self):
        # With http.
        assert get_base_url("http://example.com", include_scheme=False) == "example.com"
        assert (
            get_base_url("http://example.com/some/path", include_scheme=False)
            == "example.com"
        )
        assert (
            get_base_url("http://example.com.au/some/path", include_scheme=False)
            == "example.com.au"
        )
        # With https.
        assert (
            get_base_url("https://example.com", include_scheme=False) == "example.com"
        )
        assert (
            get_base_url("https://example.com/some/path", include_scheme=False)
            == "example.com"
        )
        assert (
            get_base_url("https://example.com.au/some/path", include_scheme=False)
            == "example.com.au"
        )

    def test_on_urls_without_scheme_returning_scheme(self):
        with warns(UserWarning):
            assert get_base_url("example.com") == "http://example.com"
            assert get_base_url("example.com/some/path") == "http://example.com"
            assert get_base_url("example.com.au/some/path") == "http://example.com.au"
            assert get_base_url("bad_url") == "http://bad_url"

    def test_on_urls_without_scheme_without_returning_scheme(self):
        with warns(UserWarning):
            assert get_base_url("example.com", include_scheme=False) == "example.com"
            assert (
                get_base_url("example.com/some/path", include_scheme=False)
                == "example.com"
            )
            assert (
                get_base_url("example.com.au/some/path", include_scheme=False)
                == "example.com.au"
            )
            assert get_base_url("bad_url", include_scheme=False) == "bad_url"
