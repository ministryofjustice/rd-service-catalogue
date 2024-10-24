<!--- Badges start --->
<img src="https://github.com/ministryofjustice/rd-service-catalogue/actions/workflows/test_pkg.yml/badge.svg" alt="Test suite status"/><img src="https://codecov.io/gh/ministryofjustice/rd-service-catalogue/graph/badge.svg?token=HPnUWIPSez" alt="Coverage report"/></a>
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

Please refer to [CONTRIBUTING.md](./CONTRIBUTING.md)
