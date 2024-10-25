"""Tests for request_utils module."""

import pytest

from ai_nexus_backend.requests_utils import _url_defence


class Test_UrlDefence:

    def test__url_defence(self):
        """Test defensive utility raises as expected."""
        # test type defence
        with pytest.raises(TypeError, match=".* found <class 'int'>"):
            _url_defence(url=1)
        with pytest.raises(TypeError, match=".* found <class 'float'>"):
            _url_defence(url=1.0)
        with pytest.raises(TypeError, match=".* found <class 'bool'>"):
            _url_defence(url=False)
        with pytest.raises(TypeError, match=".* found <class 'NoneType'>"):
            _url_defence(url=None)
        # test values
        with pytest.raises(
            ValueError, match="`url` should start with 'https://'"
        ):
            _url_defence(url="http://something")
