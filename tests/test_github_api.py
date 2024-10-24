"""Testing integration with github API."""

# flake8: noqa E501
import re
import textwrap

from mockito import when, unstub
import requests
import pytest
from yaml import YAMLError

from ai_nexus_backend import github_api


class Test_AssembleReadmeEndpointFromRepoUrl:
    """Regex pattern testing for internal utility."""

    _test_cases = [
        "https://github.com/ministryofjustice/government-digital-strategy",
        "https://github.com/ministryofjustice/moj-digital-strategy-2013",
        "https://github.com/ministryofjustice/courtfinder",
        "https://github.com/ministryofjustice/worddoc_convert",
        "https://github.com/ministryofjustice/bba",
        "https://github.com/ministryofjustice/smart-forms",
        "https://github.com/ministryofjustice/opg-loadtest",
        "https://github.com/ministryofjustice/moj_frontend_toolkit",
        "https://github.com/ministryofjustice/moj_frontend_toolkit_gem",
        "https://github.com/ministryofjustice/civil-claims-prototype",
        "https://github.com/ministryofjustice/sleepy.mongoose",
        "https://github.com/ministryofjustice/dist-wifi-mon",
        "https://github.com/ministryofjustice/opg-deputies",
        "https://github.com/ministryofjustice/opg-lpa-ruby-test",
        "https://github.com/ministryofjustice/opg-lpa-api-ruby-test",
        "https://github.com/ministryofjustice/x-moj-auth",
        "https://github.com/ministryofjustice/devise_authentication_api",
        "https://github.com/ministryofjustice/cla-can-you-get-legal-aid",
        "https://github.com/ministryofjustice/calendars",
    ]
    _expected_endpoints = [
        "https://api.github.com/repos/ministryofjustice/government-digital-strategy/readme",
        "https://api.github.com/repos/ministryofjustice/moj-digital-strategy-2013/readme",
        "https://api.github.com/repos/ministryofjustice/courtfinder/readme",
        "https://api.github.com/repos/ministryofjustice/worddoc_convert/readme",
        "https://api.github.com/repos/ministryofjustice/bba/readme",
        "https://api.github.com/repos/ministryofjustice/smart-forms/readme",
        "https://api.github.com/repos/ministryofjustice/opg-loadtest/readme",
        "https://api.github.com/repos/ministryofjustice/moj_frontend_toolkit/readme",
        "https://api.github.com/repos/ministryofjustice/moj_frontend_toolkit_gem/readme",
        "https://api.github.com/repos/ministryofjustice/civil-claims-prototype/readme",
        "https://api.github.com/repos/ministryofjustice/sleepy.mongoose/readme",
        "https://api.github.com/repos/ministryofjustice/dist-wifi-mon/readme",
        "https://api.github.com/repos/ministryofjustice/opg-deputies/readme",
        "https://api.github.com/repos/ministryofjustice/opg-lpa-ruby-test/readme",
        "https://api.github.com/repos/ministryofjustice/opg-lpa-api-ruby-test/readme",
        "https://api.github.com/repos/ministryofjustice/x-moj-auth/readme",
        "https://api.github.com/repos/ministryofjustice/devise_authentication_api/readme",
        "https://api.github.com/repos/ministryofjustice/cla-can-you-get-legal-aid/readme",
        "https://api.github.com/repos/ministryofjustice/calendars/readme",
    ]

    @pytest.mark.parametrize(
        "repo_url, endpoint_url", zip(_test_cases, _expected_endpoints)
    )
    def test__assemble_readme_endpoint_from_repo_url_returns_expected_str(
        self, repo_url, endpoint_url
    ):
        """Loop through every repo url, check func returns exp endpoint."""
        assert (
            github_api._assemble_readme_endpoint_from_repo_url(repo_url)
            == endpoint_url
        )


class TestGetReadmeContent(object):
    """Tests for get_readme_content()."""

    def test_get_readme_content_defence(self):
        """Check defensive logic."""
        with pytest.raises(
            TypeError,
            match="repo_url expected type str. Found <class 'int'>.",
        ):
            github_api.get_readme_content(
                repo_url=1, pat="foo", agent="bar"
            )
        with pytest.raises(
            ValueError,
            match=re.escape(
                "accept expects either application/vnd.github+json or app"
            ),
        ):
            github_api.get_readme_content(
                repo_url="foobar",
                pat="foo",
                agent="bar",
                accept="wrong",
            )
        with pytest.raises(
            ValueError,
            match="repo_url should begin with 'https://', found http://",
        ):
            github_api.get_readme_content(
                repo_url="http://NOT_SUPPORTED",
                pat="foo",
                agent="bar",
            )

    def test_get_readme_content(self):
        """Mocked test ensuring byte code returned as expected string."""
        # Mock the response of the get_readme_content function
        mock_response = requests.Response()
        mock_response.status_code = 200
        _b1 = b'{"content": "VGhpcyBpcyB0aGUgUkVBRE1FIGNvbnRlbnQ=",'
        _b2 = b' "encoding": "base64"}'
        _bytes = _b1 + _b2
        mock_response._content = _bytes

        # Mock the requests.get call inside get_readme_content. Needs to
        # match requests.get usage in the module.
        when(requests).get(...).thenReturn(mock_response)
        # Call & assert
        result = github_api.get_readme_content(
            "https://github.com/owner/repo", "fake_pat", "fake_agent"
        )
        assert result == "This is the README content"
        unstub()

        # repeat for accept HTML
        when(requests).get(...).thenReturn(mock_response)
        result = github_api.get_readme_content(
            "https://github.com/owner/repo",
            "fake_pat",
            "fake_agent",
            accept="application/vnd.github.html+json",
        )
        unstub()


class TestExtractYamlFromMd:
    """Tests for extract_yaml_from_md()."""

    def test_extract_valid_yaml(self):
        """Test extraction of valid YAML from Markdown content."""
        md_content = """
        # Sample README

        Here is some content.

        ```yaml
        key1: value1
        key2: value2
        ```

        More content here.
        """
        expected_output = {"key1": "value1", "key2": "value2"}
        # As the test introduces indentation to the multistring 'markdown'
        # we need to unindent here, YAML is indent aware.
        md_content = textwrap.dedent(md_content)
        assert (
            github_api.extract_yaml_from_md(md_content) == expected_output
        )

    def test_extract_first_yaml_block_only(self):
        """Test that only the first YAML block is extracted."""
        md_content = """
        # Sample README

        ```yaml
        key1: value1
        ```

        Some other content.

        ```yaml
        key2: value2
        ```
        """
        expected_output = {"key1": "value1"}
        assert (
            github_api.extract_yaml_from_md(md_content) == expected_output
        )

    def test_no_recognised_yaml_block(self):
        """Test that ValueError is raised when no YAML block is present."""
        md_content = """
        # Sample README

        Here is some content without YAML.
        """
        with pytest.raises(
            ValueError, match="No YAML found in `md_content`"
        ):
            github_api.extract_yaml_from_md(md_content)

        # This scenario is also raised on a YAML code block formatted as
        # below.
        md_content = """
        # Sample README

        ```{yaml}
        key1: value
        ```
        """
        with pytest.raises(
            ValueError, match="No YAML found in `md_content`"
        ):
            github_api.extract_yaml_from_md(md_content)

    def test_invalid_yaml(self):
        """Test that YAMLError is raised for invalid YAML content."""
        # Intentionally malformed YAML
        md_content = """
        # Sample README

        ```yaml
        key1: value1
        key2: value2
        key3: [
        - item1
        - item2
        - item3
        - unclosed array
        ```
        """
        with pytest.raises(YAMLError):
            github_api.extract_yaml_from_md(md_content)
