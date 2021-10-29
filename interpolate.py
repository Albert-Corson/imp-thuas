import pandas as pd


def interpolate(df: pd.DataFrame) -> pd.DataFrame:
    cp = df.copy()
    indices = cp.index
    cp.index = [pd.to_datetime(it) for it in cp.index]
    cp.interpolate('time', inplace=True)
    cp.index = indices
    return cp
