
"""Rule-based detection and summarization of candidate driving scenarios."""

from __future__ import annotations

import pandas as pd


def detect_scenarios(
    df: pd.DataFrame,
    braking_threshold: float = -3.0,
    acceleration_threshold: float = 3.0,
    jerk_threshold: float | None = 85.0,
    max_lane_change_gap_seconds: float = 0.5,
) -> pd.DataFrame:
    """
    Detect candidate driving scenarios in vehicle trajectory data.

    Scenarios:
    - Harsh braking
    - Rapid acceleration
    - Abrupt jerk
    - Lane changes

    Thresholds are heuristic screening rules, not validated
    definitions of dangerous driving.
    """

    required = {
        "run_index",
        "id",
        "time",
        "acceleration_kf",
        "lane_kf",
    }

    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    if not pd.api.types.is_numeric_dtype(df["time"]):
        raise TypeError("'time' must contain numeric values in seconds.")

    if not pd.api.types.is_numeric_dtype(df["acceleration_kf"]):
        raise TypeError("'acceleration_kf' must be numeric.")

    if braking_threshold >= 0:
        raise ValueError("braking_threshold must be negative.")

    if acceleration_threshold <= 0:
        raise ValueError("acceleration_threshold must be positive.")

    if jerk_threshold is not None and jerk_threshold <= 0:
        raise ValueError("jerk_threshold must be positive.")

    if max_lane_change_gap_seconds <= 0:
        raise ValueError("max_lane_change_gap_seconds must be positive.")

    # Sort observations chronologically within each vehicle and run.
    result = (
        df.copy()
        .sort_values(
            ["run_index", "id", "time"],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )

    groups = result.groupby(
        ["run_index", "id"],
        sort=False,
        dropna=False,
    )

    # Calculate jerk if it is not already available.
    if "jerk_mps3" not in result.columns:
        delta_acc = groups["acceleration_kf"].diff()
        delta_time = groups["time"].diff()

        result["jerk_mps3"] = (
            delta_acc / delta_time.where(delta_time > 0)
        )

    elif not pd.api.types.is_numeric_dtype(result["jerk_mps3"]):
        raise TypeError("'jerk_mps3' must be numeric.")

    # Harsh braking.
    result["candidate_harsh_braking"] = (
        result["acceleration_kf"] <= braking_threshold
    )

    # Rapid acceleration.
    result["candidate_rapid_acceleration"] = (
        result["acceleration_kf"] >= acceleration_threshold
    )

    # Abrupt jerk.
    if jerk_threshold is not None:
        result["candidate_abrupt_jerk"] = (
            result["jerk_mps3"].abs() >= jerk_threshold
        )
    else:
        result["candidate_abrupt_jerk"] = False

    # Detect lane transitions.
    previous_lane = groups["lane_kf"].shift()
    previous_time = groups["time"].shift()

    time_gap = result["time"] - previous_time

    valid_lane_pair = (
        result["lane_kf"].notna()
        & previous_lane.notna()
    )

    lane_changed = (
        result["lane_kf"]
        .ne(previous_lane)
        .fillna(False)
    )

    result["previous_lane"] = previous_lane

    result["candidate_lane_change"] = (
        valid_lane_pair
        & lane_changed
        & time_gap.gt(0)
        & time_gap.le(max_lane_change_gap_seconds)
    ).fillna(False)

    return result


def summarize_events(
    df: pd.DataFrame,
    max_event_gap_seconds: float = 0.5,
) -> pd.DataFrame:
    """
    Aggregate candidate observations into driving event episodes.

    Consecutive active observations are combined into one event
    if their time difference does not exceed max_event_gap_seconds.

    Each lane change is represented as an individual transition.
    Its duration is not inferred from the available observations.
    """

    if max_event_gap_seconds <= 0:
        raise ValueError("max_event_gap_seconds must be positive.")

    scenario_columns = {
        "candidate_harsh_braking": "harsh_braking",
        "candidate_rapid_acceleration": "rapid_acceleration",
        "candidate_abrupt_jerk": "abrupt_jerk",
        "candidate_lane_change": "lane_change",
    }

    missing = set(scenario_columns).difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing detection columns: {', '.join(sorted(missing))}"
        )

    required = {"run_index", "id", "time"}

    missing_required = required.difference(df.columns)

    if missing_required:
        raise ValueError(
            f"Missing required columns: "
            f"{', '.join(sorted(missing_required))}"
        )

    if not pd.api.types.is_numeric_dtype(df["time"]):
        raise TypeError("'time' must contain numeric values in seconds.")

    records = []

    grouped_vehicles = df.groupby(
        ["run_index", "id"],
        sort=False,
        dropna=False,
    )

    for (run_index, vehicle_id), vehicle in grouped_vehicles:

        vehicle = (
            vehicle
            .sort_values("time", kind="mergesort")
            .reset_index(drop=True)
        )

        for column, scenario_name in scenario_columns.items():

            active = (
                vehicle[column]
                .fillna(False)
                .astype(bool)
            )

            active_positions = [
                position
                for position, is_active in enumerate(active)
                if is_active
            ]

            if not active_positions:
                continue

            # Lane changes are individual transitions,
            # not continuous episodes.
            if scenario_name == "lane_change":

                for position in active_positions:
                    sample = vehicle.iloc[position]

                    record = {
                        "run_index": run_index,
                        "id": vehicle_id,
                        "scenario": scenario_name,
                        "start_time": sample["time"],
                        "end_time": sample["time"],
                        "event_time": sample["time"],
                        "duration_seconds": None,
                        "sample_count": 1,
                        "previous_lane": sample.get("previous_lane"),
                        "new_lane": sample.get("lane_kf"),
                    }

                    records.append(record)

                continue

            # Split active observations into separate episodes.
            episodes = []
            current_episode = []

            for position in active_positions:

                if not current_episode:
                    current_episode = [position]
                    continue

                previous_position = current_episode[-1]

                row_gap = position - previous_position

                time_gap = (
                    vehicle.loc[position, "time"]
                    - vehicle.loc[previous_position, "time"]
                )

                # Start a new episode if:
                # 1. There is an inactive observation between samples.
                # 2. The time gap is too large.
                if (
                    row_gap != 1
                    or time_gap <= 0
                    or time_gap > max_event_gap_seconds
                ):
                    episodes.append(current_episode)
                    current_episode = [position]

                else:
                    current_episode.append(position)

            if current_episode:
                episodes.append(current_episode)

            # Summarize each episode.
            for episode_positions in episodes:

                samples = vehicle.iloc[episode_positions]

                start_time = samples["time"].min()
                end_time = samples["time"].max()

                record = {
                    "run_index": run_index,
                    "id": vehicle_id,
                    "scenario": scenario_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "event_time": None,
                    "duration_seconds": end_time - start_time,
                    "sample_count": len(samples),
                    "previous_lane": None,
                    "new_lane": None,
                }

                if "acceleration_kf" in samples.columns:
                    record["min_acceleration_m_s2"] = (
                        samples["acceleration_kf"].min()
                    )

                    record["max_acceleration_m_s2"] = (
                        samples["acceleration_kf"].max()
                    )

                if "jerk_mps3" in samples.columns:
                    record["max_abs_jerk_m_s3"] = (
                        samples["jerk_mps3"].abs().max()
                    )

                if "lane_kf" in samples.columns:
                    record["lane_labels"] = ", ".join(
                        str(value)
                        for value in pd.unique(
                            samples["lane_kf"].dropna()
                        )
                    )

                records.append(record)

    columns = [
        "run_index",
        "id",
        "scenario",
        "start_time",
        "end_time",
        "event_time",
        "duration_seconds",
        "sample_count",
        "min_acceleration_m_s2",
        "max_acceleration_m_s2",
        "max_abs_jerk_m_s3",
        "lane_labels",
        "previous_lane",
        "new_lane",
    ]

    if not records:
        return pd.DataFrame(columns=columns)

    return (
        pd.DataFrame.from_records(records)
        .reindex(columns=columns)
        .sort_values(
            ["run_index", "id", "start_time", "scenario"],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )
