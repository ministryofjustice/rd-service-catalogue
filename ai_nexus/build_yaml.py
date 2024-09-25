import pathlib 

import pandas as pd


def build_listings_from_parquet(
        prq_pth:pathlib.Path,
        template_pth: pathlib.Path,
        yaml_out_pth: pathlib.Path
        ) -> None:
    """Create the yaml file required to build quarto listings.

    Requires a parquet file of repo metadata and a template.txt, containing
    the required yaml fields. 

    Parameters
    ----------
    pqr_pth: pathlib.Path
        Path to the parquet repo metadata.
    template_pth: pathlib.Path
        Path to the template.txt with required yaml fields & formatting.
    yaml_out_pth: pathlib.Path
        Path to the outfile.

    Returns
    -------
    None
    """

    with open(template_pth, "r") as f:
        template = f.read()
        f.close()
    dat = pd.read_parquet(prq_pth)
    with open(yaml_out_pth, "w") as f:
        for i, r in dat.iterrows():
            desc = r["description"]
            if desc:
                # in cases where there is a description, some people use
                # quotes and backslashes that need to be escaped/removed.
                desc = desc.replace("\\", "").replace('"', '\\"')
            yaml_entry = template.format(
                REPO_NM=r["name"].replace('"', '\\"'),
                REPO_DESC=desc,
                YYYY_MM_DD=r["updated_at"],
                REPO_URL=r["html_url"],
                ORG_NM=r["org_nm"],
                TOPIC_LIST=[
                    item for sublist in r["topics"].values() for item in sublist.tolist() # TODO - tidy this
                    ],
            )
            f.write(yaml_entry)
        f.close()
    return None
