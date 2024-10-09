"""
Example implementation for transforming data for the service catalogue into a format
that can be accepted by the Haystack/Opensearch indexing pipeline.

This script requires two arguments: one for the input json file, one for the
output.

Example of usage:
> python prep_data_for_haystack.py "ai_catalogue.json" "search_backend_data.json"

TO UPDATE
 - Currently requires data to be stored alongside this script in a file called
'ai_catalogue.json'. Eventually this should be connected to the database
underpinning the main app.
"""

import argparse
import json
from ai_nexus_backend.data_prep_utils import fetch_data, transform_data


parser = argparse.ArgumentParser(prog="Transform json data into format for Haystack")
parser.add_argument("in_path", help="Enter path to input json file")
parser.add_argument("out_path", help="Enter path to output json file")
args = parser.parse_args()

# Read the project list from a json file
project_list = fetch_data(args.in_path)
# Get into the desired format
dataset = transform_data(project_list)

# Write to another json file
with open(args.out_path, 'w') as f:
    json.dump(dataset, f, indent=4)
