"""Tests for data_prep_utils."""

from pyprojroot import here
import pytest

from ai_nexus_backend.data_prep_utils import fetch_data, transform_data


# maintain this list with expected return values for fixture in tests/data
exp_dat = [
    {
        "project_name": "Proj 1",
        "date_identified": "02/10/2024",
        "date_last_updated": None,
        "description": "Proof of concept...",
        "business_area": "HQ",
        "team": "Justice Digital",
        "using_generative_ai_llm": "Yes",
        "ai_functionality": "Generative AI",
        "status": "Proof of concept",
        "what_does_this_initiative_do": "A ...",
        "reasons_for_use": None,
        "problem_solved_by_the_initiative": "...",
        "metrics_or_intended_impacts": None,
        "lessons_learned": None,
        "future_work": None,
        "high_level_domain_estimate": None,
        "who_are_the_users": "...",
        "utilisation": None,
        "business_lead": None,
        "technical_lead": "Specified lead",
        "github_url": "...",
    },
    {
        "project_name": "Proj 2",
        "date_identified": "09/10/2024",
        "date_last_updated": None,
        "description": "Proof of concept...",
        "business_area": "HQ",
        "team": "Justice Digital",
        "using_generative_ai_llm": "Yes",
        "ai_functionality": "Generative AI",
        "status": "Proof of concept",
        "what_does_this_initiative_do": "A ...",
        "reasons_for_use": None,
        "problem_solved_by_the_initiative": "...",
        "metrics_or_intended_impacts": None,
        "lessons_learned": None,
        "future_work": None,
        "high_level_domain_estimate": None,
        "who_are_the_users": "...",
        "utilisation": None,
        "business_lead": None,
        "technical_lead": "Specified leader",
        "github_url": "...",
    },
]


class TestFetchData:
    """Testing the JSON metadata is fetched as expected.

    The JSON at this path can be used to keep any edge cases, adding
    new cases will need adding the expected return values to `exp_dat`.
    """

    json_pth = here("tests/data/metadata_example.json")
    dat = fetch_data(json_pth)

    @pytest.mark.parametrize(
        "returned_dict, expected_dict", zip(dat, exp_dat)
    )
    def test_fetch_data_return_types(self, returned_dict, expected_dict):
        """Check return values for all metadata in JSON fixture."""
        assert isinstance(
            returned_dict, dict
        ), f"Expected list of dicts, found list of {type(returned_dict)}"
        assert (
            returned_dict == expected_dict
        ), f"Expected {expected_dict}, found {returned_dict}."


class TestTransformData:
    """Testing data is formatted for haystack."""

    def test_transform_data_return_values(self):
        """Test return value of transform_data."""
        # expected list will contain one entry for every hard-coded
        # `fields_to_search` that is not None as value for content key and
        # entire metadata as dictionary for meta key.
        exp_out = [
            {
                "meta": {
                    "project_name": "Proj 1",
                    "date_identified": "02/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified lead",
                    "github_url": "...",
                    "matched_field": "project_name",
                },
                "content": "Proj 1",
            },
            {
                "meta": {
                    "project_name": "Proj 1",
                    "date_identified": "02/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified lead",
                    "github_url": "...",
                    "matched_field": "description",
                },
                "content": "Proof of concept...",
            },
            {
                "meta": {
                    "project_name": "Proj 1",
                    "date_identified": "02/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified lead",
                    "github_url": "...",
                    "matched_field": "what_does_this_initiative_do",
                },
                "content": "A ...",
            },
            {
                "meta": {
                    "project_name": "Proj 1",
                    "date_identified": "02/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified lead",
                    "github_url": "...",
                    "matched_field": "problem_solved_by_the_initiative",
                },
                "content": "...",
            },
            {
                "meta": {
                    "project_name": "Proj 2",
                    "date_identified": "09/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified leader",
                    "github_url": "...",
                    "matched_field": "project_name",
                },
                "content": "Proj 2",
            },
            {
                "meta": {
                    "project_name": "Proj 2",
                    "date_identified": "09/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified leader",
                    "github_url": "...",
                    "matched_field": "description",
                },
                "content": "Proof of concept...",
            },
            {
                "meta": {
                    "project_name": "Proj 2",
                    "date_identified": "09/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified leader",
                    "github_url": "...",
                    "matched_field": "what_does_this_initiative_do",
                },
                "content": "A ...",
            },
            {
                "meta": {
                    "project_name": "Proj 2",
                    "date_identified": "09/10/2024",
                    "date_last_updated": None,
                    "description": "Proof of concept...",
                    "business_area": "HQ",
                    "team": "Justice Digital",
                    "using_generative_ai_llm": "Yes",
                    "ai_functionality": "Generative AI",
                    "status": "Proof of concept",
                    "what_does_this_initiative_do": "A ...",
                    "reasons_for_use": None,
                    "problem_solved_by_the_initiative": "...",
                    "metrics_or_intended_impacts": None,
                    "lessons_learned": None,
                    "future_work": None,
                    "high_level_domain_estimate": None,
                    "who_are_the_users": "...",
                    "utilisation": None,
                    "business_lead": None,
                    "technical_lead": "Specified leader",
                    "github_url": "...",
                    "matched_field": "problem_solved_by_the_initiative",
                },
                "content": "...",
            },
        ]
        out = transform_data(exp_dat)
        assert isinstance(
            out, list
        ), f"Expected type `out` is list, found {type(out)}"
        assert (
            out == exp_out
        ), "Return value of `transform_data()` not as expected."
