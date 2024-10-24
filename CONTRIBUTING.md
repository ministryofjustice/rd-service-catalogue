# Developer Guidance

Install the package in editable mode with all necessary dependencies:

`pip install -e ".[dev]"`

Remember to add any additional required dependencies to the appropriate
section of the `pyproject.toml`.

When contributing to the package, please observe semantic versioning.
Increment the package version in `pyproject.toml` and update the
`CHANGELOG.md` with a high-level summary of what was added, changed,
removed or fixed.

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

Test coverage is measured using the `coverage` package. To generate a
report, first run the test suite:

`coverage run -m pytest`

Then generate a report:

`coverage report`

For a more detailed view of coverage in files, you can generate a coverage
HTML report:

`coverage html`

Then open the site rendered to the `htmlcov` directory:

`open ./htmlcov/index.html`

### To build the site:

1. Configure a virtual environment with python 3.12.
2. Activate the virtual environment.
3. Install the package with `pip install .`
4. Running the Makefile will build the data, YAML files for the listings
and render the site.
