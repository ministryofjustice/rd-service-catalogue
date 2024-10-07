import dotenv
from pyprojroot import here

from ai_nexus.build_yaml import build_listings_from_parquet

# configure secrets -------------------------------------------------------

secrets = dotenv.dotenv_values(".env")
org_nm1 = secrets["ORG_NM1"]
org_nm2 = secrets["ORG_NM2"]

for nm in [org_nm1, org_nm2]:
    in_pth = f"data/{nm}.parquet"
    out_pth = f"listings/{nm}.yaml"

    build_listings_from_parquet(
        prq_pth=here(in_pth),
        template_pth=here("template.txt"),
        yaml_out_pth=here(out_pth),
    )
