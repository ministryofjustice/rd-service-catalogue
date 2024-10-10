"""Tests for data_prep_utils."""

from pyprojroot import here
import pytest

from ai_nexus_backend.data_prep_utils import fetch_data


class TestFetchData:
    """Testing the JSON metadata is fetched as expected.

    The JSON at this path can be used to keep any edge cases, adding
    new cases will need adding the expected return values to `exp_dat`.
    """

    json_pth = here("tests/data/metadata_example.json")
    dat = fetch_data(json_pth)
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

    @pytest.mark.parametrize(
        "returned_dicts, expected_dicts", zip(dat, exp_dat)
    )
    def test_fetch_data_return_types(self, returned_dicts, expected_dicts):
        """Check return values for all metadata in JSON fixture."""
        assert isinstance(returned_dicts, dict)
        assert returned_dicts == expected_dicts
