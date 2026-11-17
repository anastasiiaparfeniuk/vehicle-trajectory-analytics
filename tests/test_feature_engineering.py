
import pandas as pd

from src.python.feature_engineering import (
    add_speed_kmh,
    add_jerk,
    add_absolute_acceleration,
)


def test_add_speed_kmh():
    df = pd.DataFrame({
        "speed_kf": [10.0, 20.0]
    })

    result = add_speed_kmh(df)

    assert result["speed_kmh"].tolist() == [36.0, 72.0]


def test_add_jerk():
    df = pd.DataFrame({
        "run_index": [1, 1, 1],
        "id": [101, 101, 101],
        "time": [0.0, 0.5, 1.0],
        "acceleration_kf": [0.0, 2.0, 4.0],
    })

    result = add_jerk(df)

    assert pd.isna(result["jerk_mps3"].iloc[0])
    assert result["jerk_mps3"].iloc[1] == 4.0
    assert result["jerk_mps3"].iloc[2] == 4.0


def test_add_absolute_acceleration():
    df = pd.DataFrame({
        "acceleration_kf": [-3.0, 2.0, 0.0]
    })

    result = add_absolute_acceleration(df)

    assert result["abs_acceleration"].tolist() == [3.0, 2.0, 0.0]
