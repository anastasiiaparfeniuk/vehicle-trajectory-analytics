import pandas as pd


def preprocess_data(df):
    df = df.copy()

    # Convert coordinate column to numeric
    df["xloc_kf"] = pd.to_numeric(
        df["xloc_kf"].astype(str).str.replace(",", "", regex=False)
    )

    # Sort observations by vehicle, run and time
    df = df.sort_values(
        by=["run_index", "id", "time"]
    ).reset_index(drop=True)

    return df
