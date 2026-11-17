
def check_data_quality(df):
    return {
        "missing_values": df.isna().sum(),
        "duplicates": df.duplicated().sum()
    }

def check_data_types(df):
    """
    Return data types of all columns.
    """
    return df.dtypes


def get_dataset_info(df):
    """
    Return basic information about the dataset.
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "unique_vehicles": df["id"].nunique(),
        "unique_runs": df["run_index"].nunique()
    }