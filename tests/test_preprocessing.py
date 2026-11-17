
import pandas as pd

from src.python.preprocessing import preprocess_data


def test_preprocess_data_converts_xloc_to_numeric():
    df = pd.DataFrame({
        "run_index": [1, 1],
        "id": [101, 101],
        "time": [0.2, 0.1],
        "xloc_kf": ["1,234.5", "1,200.0"],
    })

    result = preprocess_data(df)

    assert pd.api.types.is_numeric_dtype(result["xloc_kf"])
    assert result["xloc_kf"].tolist() == [1200.0, 1234.5]


def test_preprocess_data_sorts_observations():
    df = pd.DataFrame({
        "run_index": [1, 1, 1],
        "id": [101, 101, 101],
        "time": [0.3, 0.1, 0.2],
        "xloc_kf": ["300", "100", "200"],
    })

    result = preprocess_data(df)

    assert result["time"].tolist() == [0.1, 0.2, 0.3]
