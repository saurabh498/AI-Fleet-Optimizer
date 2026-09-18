import pytest

from ml.explainability import (
    explain_demand_prediction,
    explain_demand_from_context,
)


def _sample_row():
    return {
        "hour": 9,
        "day_of_week": 2,
        "available_loads": 25,
        "completed_loads": 18,
        "city_Mumbai": 1,
        "city_Pune": 0,
        "city_Delhi": 0,
        "city_Bengaluru": 0,
        "city_Chennai": 0,
        "city_Hyderabad": 0,
        "city_Kolkata": 0,
        "city_Ahmedabad": 0,
        "city_Surat": 0,
        "city_Jaipur": 0,
        "city_Gurgaon": 0,
        "city_Indore": 0,
        "city_Bhopal": 0,
        "city_Nagpur": 0,
    }


def test_shap_returns_prediction_and_drivers():
    result = explain_demand_prediction(_sample_row())

    assert "predicted_value" in result
    assert "base_value" in result
    assert isinstance(result["top_positive"], list)
    assert isinstance(result["top_negative"], list)
    assert isinstance(result["summary"], str)
    assert result["summary"]


def test_shap_top_positive_has_impact():
    result = explain_demand_prediction(_sample_row())

    for driver in result["top_positive"]:
        assert driver["impact"] > 0
        assert "feature" in driver
        assert "value" in driver


def test_shap_summary_mentions_prediction():
    result = explain_demand_prediction(_sample_row())
    assert "Prediction" in result["summary"]


def test_shap_missing_feature_raises():
    bad_row = {"hour": 9}
    with pytest.raises(ValueError, match="Missing features"):
        explain_demand_prediction(bad_row)


def test_context_helper_matches_prediction():
    result = explain_demand_from_context(
        city="Mumbai",
        hour=9,
        day_of_week=2,
        available_loads=25,
        completed_loads=18,
    )

    assert "predicted_value" in result
    assert result["predicted_value"] > 0
    assert len(result["top_positive"]) > 0