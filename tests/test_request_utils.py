"""Tests for request_utils module."""

import pytest

from ai_nexus_backend.requests_utils import _url_defence


class Test_UrlDefence:

    def test__url_defence(self):
        """Test defensive utility raises as expected."""
        # test type defence
        with pytest.raises(TypeError, match=".* Found <class 'int'>"):
            _url_defence(url=1, param_nm="int")
        with pytest.raises(TypeError, match=".* Found <class 'float'>"):
            _url_defence(url=1.0, param_nm="float")
        with pytest.raises(TypeError, match=".* Found <class 'bool'>"):
            _url_defence(url=False, param_nm="bool")
        with pytest.raises(TypeError, match=".* Found <class 'NoneType'>"):
            _url_defence(url=None, param_nm="Nonetype")

        # test values
        with pytest.raises(
            ValueError,
            match="url should begin with 'https://', found http://",
        ):
            _url_defence(url="http://something", param_nm="url")
