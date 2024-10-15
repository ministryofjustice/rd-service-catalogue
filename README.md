<!--- Badges start --->
<img src="https://github.com/ministryofjustice/rd-service-catalogue/actions/workflows/test_pkg.yml/badge.svg" alt="Test suite status"/>

<!--- Badges end --->

# AI Nexus

## A catalogue of products and services featuring GenAI capabilities.

### Data Privacy

**Do not commit private repository metadata to this code repository.**

Note that the app is currently configured to access public repo via a
developer's GitHub Personal Access Token (PAT). If this changes to include
private repos, then an alternative to GitHub Pages will need to be used for
hosting the site.

## Developer Guidance

This project uses [pre-commit](https://pre-commit.com/) for automated
linting. Pre-commit is installed with dev requirements in `pyproject.toml`.

Once pre-commit is installed, remember to install the hooks with:

`pre-commit install`

This step installs the hooks specified within `.pre-commit-config.yaml`.

Committing diff should now run the hooks against the files. To see hook
feedback for all files (including unstaged), run:

`pre-commit run --all-files`

### To configure your secrets:

This app requires you to set some environment variables as secrets. We use
`python-dotenv` to load these variables at runtime.

1. Create a `.env` file in the project root.
2. Update the `.env` file with the following values:

```
AGENT = "<INSERT A SUITABLE USER AGENT>"
GITHUB_PAT = "<INSERT A GITHUB PAT WITH READ REPO METADATA SCOPES>"
ORG_NM1 = "<INSERT AN ORGANISATION NAME>"
ORG_NM2 = "<INSERT AN ORGANISATION NAME>"
ATLASSIAN_PAT = "<INSERT YOUR PAT>"
ATLASSIAN_EMAIL = "<INSERT YOUR ATLASSIAN ACCOUNT EMAIL>

```

Ensure you have configured your GITHUB_PAT with SSO for organisation access
and have granted it with sufficient scopes.

Note: The order of `ORG_NM1` / `ORG_NM2` shouldn't matter.
To create an Atlassian Personal Access Token, visit
[Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

### To build the site:

1. Configure a virtual environment with python 3.12.
2. Activate the virtual environment.
3. Install the package with `pip install .`
4. Running the Makefile will build the data, YAML files for the listings
and render the site.
