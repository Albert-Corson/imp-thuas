import pandas as pd
from datetime import timedelta


def factoryzero_date_parser(df: pd.DataFrame) -> pd.DataFrame:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit='s').round('min')
    df = df.set_index("Timestamp")
    return df


config = {
    "date_parser": factoryzero_date_parser,
    "min_gap_distance": 5,
    "gaps": [
        [timedelta(minutes=5),   timedelta(hours=1),     0.15],
        [timedelta(hours=1),     timedelta(hours=6),     0.05],
        [timedelta(hours=6),     timedelta(hours=24),    0.015],
        [timedelta(hours=24),    timedelta(hours=72),    0.005],
        [timedelta(hours=72),    timedelta(hours=168),   0.001]
    ],
    "timedelta": timedelta(minutes=5)
}