import dotenv
from pyprojroot import here

from ai_nexus_backend.github_api import (
    get_org_repos,
    get_all_org_repo_metadata,
)


# configure secrets -------------------------------------------------------

secrets = dotenv.dotenv_values(".env")
user_agent = secrets["AGENT"]
pat = secrets["GITHUB_PAT"]
org_nm1 = secrets["ORG_NM1"]
org_nm2 = secrets["ORG_NM2"]


# gulp data ---------------------------------------------------------------

for nm in [org_nm1, org_nm2]:
    repos = get_org_repos(org_nm=nm, pat=pat, agent=user_agent)

    custom_props = get_all_org_repo_metadata(
        metadata="custom_properties",
        repo_nms=repos["name"],
        org_nm=nm,
        pat=pat,
        agent=user_agent,
    )

    topics = get_all_org_repo_metadata(
        metadata="topics",
        repo_nms=repos["name"],
        org_nm=nm,
        pat=pat,
        agent=user_agent,
    )

    # join tables ---------------------------------------------------------
    for tab in [repos, custom_props, topics]:
        tab.set_index("repo_url", inplace=True)
    out = repos.join(custom_props).join(topics)

    # write parquet -------------------------------------------------------
    out_pth = f"data/{nm}.parquet"
    out.to_parquet(here(out_pth))
