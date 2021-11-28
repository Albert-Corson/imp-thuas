import pandas as pd
from datetime import timedelta


def factoryzero_date_parser(df: pd.DataFrame) -> pd.DataFrame:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit='s')
    df = df.set_index("Timestamp")
    return df


config = {
    "date_parser": factoryzero_date_parser,
    "min_gap_distance": 5,
    "gaps": [
        [1,       60/5,     0.15],
        [60/5,    60/5*6,   0.05],
        [60/5*6,  60/5*24,  0.015],
        [60/5*24, 60/5*72,  0.005],
        [60/5*72, 60/5*168, 0.001]
    ],
    "timedelta": timedelta(minutes=5)
}