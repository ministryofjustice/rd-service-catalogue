"""
Functions to help transform data for the service catalogue into a format that can
be accepted by the Haystack/Opensearch indexing pipeline.

TO UPDATE
 - The columns to search over are hard-coded
"""

import json


def fetch_data(fname: str) -> list:

    """
    Read data from a json file into a list. Perform some basic data cleaning.

    Args
    :fname: Name/path of the json file to be read in

    Return
    A list containing dictionaries with details of projects to include in the catalogue.
    """

    with open(fname) as f:
        project_list = json.load(f)


    # Replace newlines as they interfere with the matching
    project_list = [
        {k : v.replace('\n', ' ') if v is not None else v for k, v in project.items()}
        for project in project_list
    ]

    return project_list


def _format_doc_dict(doc: dict, field: str) -> dict:

    """
    Reformat data into format accepted by Haystack.
    Here we wish to search over multiple fields, so we include the text from different
    fields in separate dictionaries within a list.

    Args
    :doc: dictionary containing text data to search along with accompanying metadata
    :field: string corresponding to one of the dictionary keys, to indicate the field to index the text from

    Return
    Dictionary containing two fields: 1) content to be searched (a string), and 2) metadata (another dictionary)
    """

    content = doc[field]
    # doc.pop(field)

    if content is None:
        # We can't index None values, so returning None here allows us to skip fields where no info is provided
        return None
    else:
        meta = doc.copy()
        meta['matched_field'] = field

        doc_dict = {
            'meta': meta,
            'content': content,
        }

        return doc_dict


def transform_data(project_list: list) -> list:
    """
    Transform the data underpinning the search engine by putting separate fields
    to search over in separate dictionaries.

    Args
    :project_list: List of dictionaries containing project details

    Return
    List of dictionaries, one for each field to search over for each project.
    """

    # If the data contains multiple fields we'd want to search over, list them here
    fields_to_search = [
        'project_name',
        'description',
        'what_does_this_initiative_do',
        'reasons_for_use',
        'problem_solved_by_the_initiative',
        'metrics_or_intended_impacts'
    ]

    # Iterate through the list of projects and reformat to more easily allow us to search
    # over multiple fields
    dataset = [
        y for project in project_list for field in fields_to_search
        if (y := _format_doc_dict(project, field)) is not None
    ]

    return dataset
