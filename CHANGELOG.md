# `ai_nexus_backend` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-02-20

### Added

- GithubClient._paginated_request has new logic for requesting commits
within a time window of interest. Specifying a value for
`timedelta_cutoff_days` means commits older than this value will not be
returned.
- GitHubClient.get_commits_for_html_url conveniently wraps the above so
that all commits within a time window of interest can be returned for a
given url.

## [0.3.0] - 2024-12-10

### Added

- GitHubClient.get_repo_metadata
    - Gets metadata for a single repo HTML URL.
    - Topics and custom properties supported.

### Changed

- GitHubClient.get_all_org_repo_metadata -> GitHubClient.get_all_repo_metadata
    - New implementation takes a list of HTML URLs instead of repo and
    organisation names.

## [0.2.1] - 2024-11-15

### Added

- `ai_nexus_backend.github_api.get_org_repos` now returns repository ID.

### Changed

- Refactor request exception handling

## [0.2.0] - 2024-10-28

### Added

- Introduces `extract_yaml_metadata()` method to
`ai_nexus_backend.confluence_api.ConfluenceClient`.
- Coverage checks in CI.
- Implementation examples in `notebooks` directory.

### Changed

- `ai_nexus_backend.confluence_api.ConfluenceClient` refactored method
`_find_code_metadata()` to `extract_json_metadata()`.
- Introduces `GitHubClient` to `ai_nexus_backend.github_api`. More
efficient storing of authentication credentials.

## [0.1.1] - 2024-10-15

### Added

- `ai_nexus_backend.github_api.extract_yaml_from_md` matches YAML chunks
embedded in README.md content strings.

## [0.1.0] - 2024-10-10

### Added

- Changelog
- `ai_nexus_backend.data_prep_utils` formats JSON metadata for `haystack`.
- Increased python compatibility range & build checks.
- Package name updated from `ai_nexus` to `ai_nexus_backend`.
- `ai_nexus.confluence_api` ingests content from Confluence pages.
- `ai_nexus.github_api` ingests GitHub repo README.md content.
- `pre-commit` checks and GitHub Actions workflows.

## [0.0.1] - 2023-09-25

### Added

- Automated build for proof-of-concept (PoC) frontend - not maintained.
- Multiple iterations for PoC site - not maintained.
- Utility functions for PoC site under `ai_nexus.build_yaml`.
- GitHub API integration logic under `ai_nexus.github_api`. Grab all
repositories for an organisation. Grab all issues or PRs for a list of
repos.
