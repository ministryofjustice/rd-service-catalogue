"""Query GitHub api."""

from base64 import b64decode
import re

import pandas as pd
import requests
from requests.exceptions import HTTPError
from yaml import safe_load, YAMLError

from ai_nexus_backend.requests_utils import _configure_requests


def _paginated_get(
    url: str,
    pat: str,
    agent: str,
    params: dict = {},
    sess: requests.Session = _configure_requests(),
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
        _configure_requests() with default values of n=5, backoff_f=0.1,
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
    page = 1
    responses = list()
    while True:
        print(f"Requesting page {page}")
        params["page"] = page
        r = sess.get(
            url,
            headers={
                "Authorization": f"Bearer {pat}",
                "User-Agent": agent,
            },
            params=params,
        )
        if r.ok:
            responses.append(r.json())
            if "next" in r.links:
                url = r.links["next"]["url"]
                page += 1
            else:
                # no more next links so stop while loop
                print(
                    "Requests left: " + r.headers["X-RateLimit-Remaining"]
                )
                break
        elif r.status_code == 401:
            raise PermissionError(
                "PAT is invalid. Try generating a new PAT."
            )
        else:
            print(f"Unable to get repo issues, code: {r.status_code}")
    return responses


def get_org_repos(
    org_nm: str,
    pat: str,
    agent: str,
    sess: requests.Session = _configure_requests(),
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
        _configure_requests() with default values of n=5, backoff_f=0.1,
        force_on=[500, 502, 503, 504]
    public_only : bool
        If the GitHub PAT has private scopes for the organisation you are
        requesting, then private repo metadata will also be returned. To
        filter to public repo matadata only, set this parameter to True.
        Defaults to False.

    Returns
    -------
    pd.DataFrame
        Table of repo metadat.

    """
    # GitHub API endpoint to list pull requests for the organization
    org_repos_url = f"https://api.github.com/orgs/{org_nm}/repos"
    params = {}
    if public_only:
        params["type"] = "public"

    responses = _paginated_get(
        org_repos_url, sess=sess, pat=pat, params=params, agent=agent
    )
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
    metadata: str,
    repo_nms: list,
    org_nm: str,
    pat: str,
    agent: str,
    sess: requests.Session = _configure_requests(),
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
        _configure_requests() with default values of n=5, backoff_f=0.1,
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
    m = metadata.lower().replace(" ", "")
    if m == "custom_properties":
        url_slug = "properties/values"
    elif m == "topics":
        url_slug = m
    else:
        raise NotImplementedError(
            "Only metadata 'custom_properties' and 'topics' are supported"
        )

    all_meta = pd.DataFrame()
    n_repos = len(repo_nms)
    for i, repo_nm in enumerate(repo_nms):
        print(f"Get {m} for {repo_nm}, {i+1}/{n_repos} done.")
        repo_url = f"https://api.github.com/repos/{org_nm}/{repo_nm}"
        query_url = f"{repo_url}/{url_slug}"
        PARAMS = {"accept": "application/vnd.github+json"}
        repo_meta = sess.get(
            query_url,
            headers={
                "Authorization": f"Bearer {pat}",
                "User-Agent": agent,
            },
            params=PARAMS,
        )
        current_row = pd.DataFrame(
            {"repo_url": repo_url, m: [repo_meta.json()]}
        )
        # TODO: conditional handling of topics vs custom properties
        all_meta = pd.concat([all_meta, current_row])

    return all_meta


def get_all_org_issues(
    repo_nms: list,
    org_nm: str,
    pat: str,
    agent: str,
    issue_type="issues",
    sess: requests.Session = _configure_requests(),
) -> pd.DataFrame:
    """Get every repo issue for entire org.

    Will work for issues or pulls. Returns a table of all issues metadata.

    Parameters
    ----------
    repo_nms : list,
        List of the repo name strings
    org_nm : str,
        The name of the org, by default ORG_NM (from .secrets.toml)
    pat : str,
        User's PAT code, by default PAT (from .secrets.toml)
    agent : str,
        User agent string, by default USER_AGENT (from .secrets.toml)
    issue_type : str, optional
        Accepts either 'issues' or 'pulls', by default "issues"
    sess : requests.Session, optional
        Session configured with retry strategy, by default
        _configure_requests() with default values of n=5, backoff_f=0.1,
        force_on=[500, 502, 503, 504]

    Returns
    -------
    list
        List of JSON content with metadata for each issue (or PR)

    Raises
    ------
    ValueError
        `issue_type` is not either 'issues' or 'pulls'

    """
    issue_type = issue_type.lower().strip()
    if "issue" in issue_type:
        endpoint = "issues"
    elif "pull" in issue_type:
        endpoint = "pulls"
    else:
        raise ValueError(
            "`issue_type` must be either 'issues' or 'pulls'."
        )

    base_url = f"https://api.github.com/repos/{org_nm}/"
    all_issues = list()
    n_repos = len(repo_nms)
    for i, nm in enumerate(repo_nms):
        print(f"Get issues for {nm}, {i+1}/{n_repos} done.")
        repo_issues = _paginated_get(
            f"{base_url}{nm}/{endpoint}", pat=pat, agent=agent
        )
        all_issues.extend(repo_issues)

    # ensure consistent dtypes
    DTYPES = {
        "repo_url": str,
        "issue_id": int,
        "node_id": str,
        "title": str,
        "body": str,
        "number": int,
        "labels": str,
        "assignees_logins": str,
        "assignees_avatar_urls": str,
        "created_at": str,
        "user_name": str,
        "user_avatar": str,
    }

    repo_issues_concat = pd.DataFrame()
    for issue in all_issues:
        # catch empty responses where repos have no PRs
        if len(issue) == 0:
            continue
        else:
            for i in issue:
                # pull assignees over assignee, both fields are populated
                assignees = i["assignees"]
                if len(assignees) == 0:
                    assignees_users = None
                    assignees_avatar = None
                else:
                    assignees_users = [usr["login"] for usr in assignees]
                    assignees_avatar = [
                        usr["avatar_url"] for usr in assignees
                    ]
                # collect issue details
                if endpoint == "issues":
                    repo_url = i["repository_url"]
                else:
                    repo_url = i["url"]

                issue_row = pd.DataFrame.from_dict(
                    {
                        "repo_url": [repo_url],
                        "issue_id": [i["id"]],
                        "node_id": [i["node_id"]],
                        "title": [i["title"]],
                        "body": [i["body"]],
                        "number": [i["number"]],
                        "labels": [
                            ", ".join([lb["name"] for lb in i["labels"]])
                        ],
                        "assignees_logins": [assignees_users],
                        "assignees_avatar_urls": [assignees_avatar],
                        "created_at": [i["created_at"]],
                        "user_name": [i["user"]["login"]],
                        "user_avatar": [i["user"]["avatar_url"]],
                    }
                )
                # Set dtypes for each column
                for col, dtype in DTYPES.items():
                    issue_row[col] = issue_row[col].astype(dtype)

                repo_issues_concat = pd.concat(
                    [repo_issues_concat, issue_row]
                )

    repo_issues_concat.sort_values(by="created_at", inplace=True)

    return repo_issues_concat


def combine_repo_tables(
    repo_table: pd.DataFrame,
    issues_table: pd.DataFrame,
    pulls_table: pd.DataFrame,
) -> pd.DataFrame:
    """Combine the three tables to provide a single coherent output.

    Parameters
    ----------
    repo_table : pd.DataFrame
        Output of get_org_repos().
    issues_table : pd.DataFrame
        Output of get_all_org_issues(repo_nms=all_repo_deets["name"],
        issue_type="issues")
    pulls_table : pd.DataFrame
        Output of get_all_org_issues(repo_nms=all_repo_deets["name"],
        issue_type="pulls")

    Returns
    -------
    pd.DataFrame
        Issues and PRs are concatenated with a 'type' marker. Single table
        joined with repo_table to give full context of each issue or PR.

    """
    reps = repo_table.copy(deep=True).reset_index(drop=True)
    iss = issues_table.copy(deep=True).reset_index(drop=True)
    pulls = pulls_table.copy(deep=True).reset_index(drop=True)
    # the pull table repo_url is not consistent with the issue table
    # repo_url. pattern is repo_url/pulls/pull_no
    pulls["repo_url"] = [
        i.split("pulls")[0][:-1] for i in pulls["repo_url"]
    ]
    pulls["type"] = "pr"
    # filter down the issues table, which contains pulls too, and no
    # obvious identifier
    issues_pulls = iss.merge(
        pulls, how="left", on="node_id", indicator=True
    )["_merge"]
    iss = issues_table.loc[issues_pulls == "left_only"]
    iss["type"] = "issue"
    # combine issues & pulls
    output_table = pd.concat([iss, pulls], ignore_index=True)
    output_table = output_table.merge(reps, how="left", on="repo_url")

    return output_table


def _assemble_readme_endpoint_from_repo_url(repo_url: str):
    """Match owner & repo names from GitHub url. Return readme endpoint.

    Created to help testing regex pattern.
    """
    # see https://regex101.com/r/KrKdEj/1 for test cases...
    cap_groups = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    owner = cap_groups.group(1)
    repo_nm = cap_groups.group(2)
    return f"https://api.github.com/repos/{owner}/{repo_nm}/readme"


def get_readme_content(
    repo_url: str,
    pat: str,
    agent: str,
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
        "application/vnd.github+json" or "application/vnd.github.html+json"
        or if the `repo_url` does not start with "https://".
    requests.exceptions.HTTPError
        If the HTTP request to the GitHub API fails.
    """
    # defence
    str_params = {
        "repo_url": repo_url,
        "pat": pat,
        "agent": agent,
        "accept": accept,
    }
    for k, v in str_params.items():
        if not isinstance(v, str):
            raise TypeError(f"{k} expected type str. Found {type(v)}.")
    accept_vals = [
        "application/vnd.github+json",
        "application/vnd.github.html+json",
    ]
    if accept not in accept_vals:
        raise ValueError(
            f"accept expects either {' or '.join(accept_vals)}"
        )
    if not repo_url.startswith("https://"):
        raise ValueError(
            f"repo_url should begin with 'https://', found {repo_url[0:7]}"
        )
    params = {"accept": accept}
    endpoint = _assemble_readme_endpoint_from_repo_url(repo_url)
    resp = requests.get(
        endpoint,
        params=params,
        headers={"Authorization": f"Bearer {pat}", "User-Agent": agent},
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
        raise HTTPError(f"HTTP error {resp.status_code}: {resp.reason}")
    # TODO: _handle_response_exception()
    return readme


def extract_yaml_from_md(md_content: str) -> dict:
    """
    Extract the first YAML block from Markdown content string.

    If several YAML code blocks are included within the README, only the
    first will be returned. Will not match YAML code blocks with
    ```{yaml}...``` syntax.

    Parameters
    ----------
    md_content : str
        A string containing Markdown content, which may include YAML code
        blocks.

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
