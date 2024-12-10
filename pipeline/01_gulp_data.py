import dotenv
from pyprojroot import here

from ai_nexus_backend.github_api import GithubClient

# set to True for chatty outputs
debug = False
# configure secrets -------------------------------------------------------

secrets = dotenv.dotenv_values(".env")
user_agent = secrets["AGENT"]
pat = secrets["GITHUB_PAT"]
org_nm1 = secrets["ORG_NM1"]
org_nm2 = secrets["ORG_NM2"]

client = GithubClient(github_pat=pat, user_agent=user_agent)

# gulp data ---------------------------------------------------------------
# reversing order for troubleshooting purposes
for nm in [org_nm2, org_nm1]:
    repos = client.get_org_repos(
        org_nm=nm,
        public_only=True,
        debug=debug,
    )

    custom_props = client.get_all_repo_metadata(
        html_urls=repos["html_url"],
        metadata="custom_properties",
    )

    topics = client.get_all_repo_metadata(
        html_urls=repos["html_url"],
        metadata="topics",
    )

    # join tables ---------------------------------------------------------
    for tab in [repos, custom_props, topics]:
        tab.set_index("repo_url", inplace=True)
    out = repos.join(custom_props).join(topics)

    # write parquet -------------------------------------------------------
    out_pth = f"data/{nm}.parquet"
    out.to_parquet(here(out_pth))
