import pandas as pd
from datetime import timedelta


def knmi_date_parser(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index(["Date(YYYYMMDD)", "Hour"])
    def transform_index(index):
        date, hour = index
        return pd.to_datetime(str(date) + str(hour - 1), format='%Y%m%d%H')
    df = df.set_index(df.index.map(transform_index))
    return df


config = {
    "date_parser": knmi_date_parser,
    "min_gap_distance": 1,
    "gaps": [
        [1,  6,   0.15],
        [6,  24,  0.05],
        [24, 72,  0.015],
        [72, 168, 0.005]
    ],
    "timedelta": timedelta(hours=1)
}