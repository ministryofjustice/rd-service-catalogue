"""Query GitHub api."""

from base64 import b64decode
import re
import warnings

import pandas as pd

# import requests
from requests.exceptions import HTTPError
from yaml import safe_load, YAMLError

from ai_nexus_backend.requests_utils import (
    _configure_requests,
    _url_defence,
)


class GithubClient:

    def __init__(self, github_pat, user_agent=None):
        self.__pat = github_pat
        self.__agent = user_agent
        self._session = self._configure_github()

    def _configure_github(self, _session=_configure_requests()):
        """Set up a GitHub request Session with retry & backoff spec."""
        _session.headers = {
            "Authorization": f"Bearer {self.__pat}",
            "User-Agent": self.__agent,
        }
        _session.params = {"accept": "application/vnd.github+json"}
        self._session = _session
        return _session

    def _paginated_get(
        self,
        url: str,
        # pat: str,
        # agent: str,
        # params: dict = {},
        # sess: requests.Session = _configure_requests(),
    ) -> list:
        """Get paginated responses.

        Parameters
        ----------
        url : str
            The url string to query.
        pat : str,
            The User's GitHub PAT.
        agent : str,
            User's browser agent.
        params: dict
            Dictionary of parameters to pass the developer API.
        sess : requests.Session, optional
            Session configured with retry strategy, by default
            _configure_requests() default values of n=5, backoff_f=0.1,
            force_on=[500, 502, 503, 504]

        Returns
        -------
        list
            A nested list containing the response JSON content.

        Raises
        ------
        PermissionError
            The PAT is not recognised by GitHub.

        """
        sess = self._session
        page = 1
        responses = list()
        while True:
            print(f"Requesting page {page}")
            sess.params["page"] = page
            # params["page"] = page
            # r = sess.get(
            #     url,
            #     headers={
            #         "Authorization": f"Bearer {pat}",
            #         "User-Agent": agent,
            #     },
            #     params=params,
            # )
            r = sess.get(url)
            if r.ok:
                responses.append(r.json())
                if "next" in r.links:
                    url = r.links["next"]["url"]
                    page += 1
                else:
                    # no more next links so stop while loop
                    print(
                        "Requests left: "
                        + r.headers["X-RateLimit-Remaining"]
                    )
                    break
            elif r.status_code == 401:
                raise PermissionError(
                    "PAT is invalid. Try generating a new PAT."
                )
            elif r.status_code == 403:
                warnings.warn(
                    f"Skipping {url}: status {r.status_code}, {r.reason}"
                )
                continue
            else:
                print(f"Unable to get repo issues, code: {r.status_code}")
        return responses

    def get_org_repos(
        self,
        org_nm: str,
        # pat: str,
        # agent: str,
        # sess: requests.Session = _configure_requests(),
        public_only: bool = False,
    ) -> pd.DataFrame:
        """Get repo metadata for all repos in a GitHub organisation.

        Parameters
        ----------
        org_nm : str,
            The organisation name, by default ORG_NM (read from .env)
        pat : str,
            GitHub user PAT
        agent : str,
            User agent, by default USER_AGENT
        sess : requests.Session, optional
            Session configured with retry strategy, by default
            _configure_requests() default values of n=5, backoff_f=0.1,
            force_on=[500, 502, 503, 504]
        public_only : bool
            If the GitHub PAT has private scopes for the organisation you
            are requesting, then private repo metadata will also be
            returned. To filter to public repo matadata only, set this
            parameter to True. Defaults to False.

        Returns
        -------
        pd.DataFrame
            Table of repo metadat.

        """
        sess = self._session
        # GitHub API endpoint to list pull requests for the organization
        org_repos_url = f"https://api.github.com/orgs/{org_nm}/repos"
        params = {}
        if public_only:
            params["type"] = "public"

        # responses = self._paginated_get(
        #     org_repos_url, sess=sess, pat=pat, params=params, agent=agent
        # )
        responses = self._paginated_get(org_repos_url, sess=sess)
        DTYPES = {
            "html_url": str,
            "repo_url": str,
            "is_private": bool,
            "is_archived": bool,
            "name": str,
            "description": str,
            "programming_language": str,
        }
        all_repo_deets = pd.DataFrame()

        for i in responses:
            for j in i:
                repo_deets = pd.DataFrame(
                    {
                        "html_url": [j["html_url"]],
                        "repo_url": [j["url"]],
                        "is_private": [j["private"]],
                        "is_archived": [j["archived"]],
                        "name": [j["name"]],
                        "description": [j["description"]],
                        "programming_language": [j["language"]],
                        "updated_at": [j["updated_at"]],
                        "org_nm": org_nm,
                    }
                )
                # set dtypes
                for col, dtype in DTYPES.items():
                    repo_deets[col].astype(dtype)

                all_repo_deets = pd.concat([all_repo_deets, repo_deets])

        return all_repo_deets

    def get_all_org_repo_metadata(
        self,
        metadata: str,
        repo_nms: list,
        org_nm: str,
        # pat: str,
        # agent: str,
        # sess: requests.Session = _configure_requests(),
    ) -> pd.DataFrame:
        """Get every repo metadata item for entire org.

        Currently only supports metadata values "custom_properties" or
        "topics".

        Parameters
        ----------
        metadata: str
            Either "custom_properties" or "topics".
        repo_nms : list,
            List of the repo name strings
        org_nm : str,
            The name of the organisation, by default ORG_NM (from .env)
        pat : str,
            User's PAT code, by default PAT (from .env)
        agent : str,
            User agent string, by default USER_AGENT (from .secrets.toml)
        sess : requests.Session, optional
            requests.Session configured with retry strategy, by default
            _configure_requests() default values of n=5, backoff_f=0.1,
            force_on=[500, 502, 503, 504]

        Returns
        -------
        list
            List of JSON content with metadata for each issue (or PR)

        Raises
        ------
        ValueError
            `metadata` is not either 'custom_properties' or 'topics'.

        """
        m = metadata.lower().strip()
        if m == "custom_properties":
            url_slug = "properties/values"
        elif m == "topics":
            url_slug = m
        else:
            raise NotImplementedError(
                "Metadata 'custom_properties' and 'topics' are supported"
            )

        all_meta = pd.DataFrame()
        n_repos = len(repo_nms)
        for i, repo_nm in enumerate(repo_nms):
            print(f"Get {m} for {repo_nm}, {i+1}/{n_repos} done.")
            repo_url = f"https://api.github.com/repos/{org_nm}/{repo_nm}"
            query_url = f"{repo_url}/{url_slug}"
            # PARAMS = {"accept": "application/vnd.github+json"}
            # repo_meta = sess.get(
            #     query_url,
            #     headers={
            #         "Authorization": f"Bearer {pat}",
            #         "User-Agent": agent,
            #     },
            #     params=PARAMS,
            # )
            repo_meta = self._session.get(query_url)
            current_row = pd.DataFrame(
                {"repo_url": repo_url, m: [repo_meta.json()]}
            )
            all_meta = pd.concat([all_meta, current_row])

        return all_meta

    def _assemble_readme_endpoint_from_repo_url(self, repo_url: str):
        """Match owner & repo names from repo url. Return readme endpoint.

        Created to help testing regex pattern.
        """
        _url_defence(repo_url)
        # see https://regex101.com/r/KrKdEj/1 for test cases...
        cap_groups = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        owner = cap_groups.group(1)
        repo_nm = cap_groups.group(2)
        return f"https://api.github.com/repos/{owner}/{repo_nm}/readme"

    def get_readme_content(
        self,
        repo_url: str,
        # pat: str,
        # agent: str,
        accept: str = "application/vnd.github+json",
    ):
        """Fetches the README content from a single GitHub repository.

        Parameters
        ----------
        repo_url : str
            The URL of the GitHub repository.
        pat : str
            The personal access token for GitHub API authentication.
        agent : str
            The user agent string to be sent with the request.
        accept : str, optional
            The media type to accept in the response. Defaults to
            "application/vnd.github+json".

        Returns
        -------
        str
            The content of the README file.

        Raises
        ------
        TypeError
            If any of the parameters are not of type `str`.
        ValueError
            If the `accept` parameter is not one of
            "application/vnd.github+json" or
            "application/vnd.github.html+json" or if the `repo_url` does
            not start with "https://".
        requests.exceptions.HTTPError
            If the HTTP request to the GitHub API fails.
        """
        # defence
        _url_defence(repo_url)
        if not isinstance(accept, str):
            raise TypeError(
                f"accept expected type str. Found {type(accept)}"
            )
        accept_vals = [
            "application/vnd.github+json",
            "application/vnd.github.html+json",
        ]
        if accept not in accept_vals:
            raise ValueError(
                f"accept expects either {' or '.join(accept_vals)}"
            )
        params = {"accept": accept}
        endpoint = self._assemble_readme_endpoint_from_repo_url(repo_url)
        # resp = requests.get(
        #     endpoint,
        #     params=params,
        #     headers={
        # "Authorization": f"Bearer {pat}", "User-Agent": agent},
        # )
        resp = self._session.get(
            endpoint,
            params=params,
        )
        if resp.ok:
            content = resp.json()
            # decode from base64
            if (
                "content" in content.keys()
                and content.get("encoding") == "base64"
            ):
                readme = b64decode(content.get("content")).decode("utf-8")
        else:
            raise HTTPError(
                f"HTTP error {resp.status_code}: {resp.reason}"
            )
        # TODO: _handle_response_exception()
        return readme

    def extract_yaml_from_md(self, md_content: str) -> dict:
        """
        Extract the first YAML block from Markdown content string.

        If several YAML code blocks are included within the README, only
        the first will be returned. Will not match YAML code blocks with
        ```{yaml}...``` syntax.

        Parameters
        ----------
        md_content : str
            A string containing Markdown content, which may include YAML
            code blocks.

        Returns
        -------
        dict
            A dictionary containing the parsed YAML content with keys in
            lowercase.

        Raises
        ------
        ValueError
            If no YAML block is found in the provided Markdown content.
        yaml.YAMLError
            If there is an error parsing the YAML content.

        """
        # Regular expression pattern to match the FIRST fenced YAML block
        # won't match curly braces: https://regex101.com/r/oYHdwB/1
        # though curly braces are valid github MD YAML blocks:
        # https://github.com/r-leyshon/example_yaml-_metadata
        yaml_block_pattern = re.compile(r"```yaml([\s\S]*?)```")

        # Search for the first YAML block
        match = yaml_block_pattern.search(md_content)
        if match:
            yaml_content = match.group(1).strip()
            try:
                # Parse the first YAML content block
                yam = safe_load(yaml_content)
                return {k.lower(): v for k, v in yam.items()}
            except YAMLError as e:
                raise YAMLError("Error parsing YAML content:", e)
        else:
            raise ValueError("No YAML found in `md_content`")
