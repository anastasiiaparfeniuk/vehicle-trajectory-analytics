
import pandas as pd


def add_speed_kmh(df):
    """Convert vehicle speed from m/s to km/h."""
    df = df.copy()
    df["speed_kmh"] = df["speed_kf"] * 3.6

    return df


def add_jerk(df):
    """Calculate the rate of change of acceleration."""
    df = df.copy()

    groups = df.groupby(["run_index", "id"])

    delta_acc = groups["acceleration_kf"].diff()
    delta_time = groups["time"].diff()

    df["jerk_mps3"] = delta_acc / delta_time.where(delta_time > 0)

    return df


def add_absolute_acceleration(df):
    """Calculate absolute acceleration."""
    df = df.copy()
    df["abs_acceleration"] = df["acceleration_kf"].abs()

    return df


def engineer_features(df):
    """Apply all feature engineering transformations."""
    df = df.copy()

    df = add_speed_kmh(df)
    df = add_jerk(df)
    df = add_absolute_acceleration(df)

    return df
