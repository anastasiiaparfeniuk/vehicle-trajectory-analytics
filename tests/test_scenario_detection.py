
import pandas as pd

from src.python.scenario_detection import (
    detect_scenarios,
    summarize_events,
)


def test_detect_harsh_braking():
    df = pd.DataFrame({
        "run_index": [1, 1, 1],
        "id": [101, 101, 101],
        "time": [0.0, 0.1, 0.2],
        "acceleration_kf": [0.0, -3.5, -1.0],
        "lane_kf": [2, 2, 2],
    })

    result = detect_scenarios(df, jerk_threshold=None)

    assert result["candidate_harsh_braking"].tolist() == [
        False, True, False
    ]


def test_detect_rapid_acceleration():
    df = pd.DataFrame({
        "run_index": [1, 1],
        "id": [101, 101],
        "time": [0.0, 0.1],
        "acceleration_kf": [0.0, 3.5],
        "lane_kf": [2, 2],
    })

    result = detect_scenarios(df, jerk_threshold=None)

    assert result["candidate_rapid_acceleration"].tolist() == [
        False, True
    ]


def test_detect_lane_change():
    df = pd.DataFrame({
        "run_index": [1, 1],
        "id": [101, 101],
        "time": [0.0, 0.1],
        "acceleration_kf": [0.0, 0.0],
        "lane_kf": [2, 3],
    })

    result = detect_scenarios(df, jerk_threshold=None)

    assert result["candidate_lane_change"].tolist() == [
        False, True
    ]


def test_summarize_events():
    df = pd.DataFrame({
        "run_index": [1, 1, 1],
        "id": [101, 101, 101],
        "time": [0.0, 0.1, 0.2],
        "acceleration_kf": [-1.0, -3.5, -4.0],
        "jerk_mps3": [0.0, 1.0, 1.0],
        "candidate_harsh_braking": [False, True, True],
        "candidate_rapid_acceleration": [False, False, False],
        "candidate_abrupt_jerk": [False, False, False],
        "candidate_lane_change": [False, False, False],
        "previous_lane": [None, None, None],
    })

    events = summarize_events(df)

    assert len(events) == 1
    assert events.iloc[0]["scenario"] == "harsh_braking"
    assert events.iloc[0]["sample_count"] == 2
