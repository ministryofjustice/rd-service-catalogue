<!--- Badges start --->
<img src="https://github.com/ministryofjustice/rd-service-catalogue/actions/workflows/test_pkg.yml/badge.svg" alt="Test suite status"/>

<!--- Badges end --->

# `ai_nexus_backend`

## ETL for a catalogue of products and services featuring GenAI capabilities.

### Data Privacy

**Do not commit private repository metadata to this code repository.**

Note that the app is currently configured to access public repo via a
developer's GitHub Personal Access Token (PAT). If this changes to include
private repos, then an alternative to GitHub Pages will need to be used for
hosting the site.

## Installation

To install `ai_nexus_backend`:

Create a python virtual environment with your preferred method, ensuring
the python version matches the following supported versions:

- 3.9
- 3.10
- 3.11
- 3.12

For example, if using `conda`:

`conda create -n <INSERT_ENV_NM> python=3.9 -y`

Activate your env:

`conda activate <INSERT_ENV_NM>`

Once activated, install the package:

`pip install .`

## Developer Guidance

Install the package in editable mode with all necessary dependencies:

`pip install -e ".[dev]"`

Remember to add any additional required dependencies to the appropriate
section of the `pyproject.toml`.

This project uses [pre-commit](https://pre-commit.com/) for automated
linting. Pre-commit is installed with dev requirements in `pyproject.toml`.

Once pre-commit is installed, remember to install the hooks with:

`pre-commit install`

This step installs the hooks specified within `.pre-commit-config.yaml`.

Committing diff should now run the hooks against the files. To see hook
feedback for all files (including unstaged), run:

`pre-commit run --all-files`

### Quick start setup

Working on the app relies on Python dependencies being installed locally.
First set up a virtualenv and install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -e '.[dev, ai_nexus_backend]'
pre-commit install
```

### To configure your secrets:

This app requires you to set some environment variables as secrets. We use
`python-dotenv` to load these variables at runtime.

1. Create a `.env` file in the project root.
2. Update the `.env` file with the following values:

```
AGENT = "<INSERT A SUITABLE USER AGENT>"
PAT = "<INSERT A GITHUB PAT WITH READ REPO METADATA SCOPES>"
ORG_NM1 = "<INSERT AN ORGANISATION NAME>"
ORG_NM2 = "<INSERT AN ORGANISATION NAME>"
ATLASSIAN_PAT = "<INSERT YOUR PAT>"
ATLASSIAN_EMAIL = "<INSERT YOUR ATLASSIAN ACCOUNT EMAIL>

```

Note: The order of `ORG_NM1` / `ORG_NM2` shouldn't matter.
To create an Atlassian Personal Access Token, visit
[Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

### A note on testing

This package uses `pytest` to verify unit behaviour. This is set up to run
on push and PR on all branches of the repository with GitHub Actions.

Changes to the codebase will be tested on supported python versions
(see above).

To run the tests locally from the cli:

`pytest`

`pytest` can be invoked in many ways to target specific tests or groups of
tests. For more, see
[How to invoke pytest](https://docs.pytest.org/en/stable/how-to/usage.html).

### To build the site:

1. Configure a virtual environment with python 3.12.
2. Activate the virtual environment.
3. Install the package with `pip install .`
4. Running the Makefile will build the data, YAML files for the listings
and render the site.
