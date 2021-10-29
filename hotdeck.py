import pandas as pd
from pipeline import parse_uploaded_file


def load_donnor(filepath: str, index_column: str, column_to_impute: str, start_timestamp: int, end_timestamp: int):
    with open(filepath, 'rb') as file:
        buffer = file.read()
    donnor = parse_uploaded_file(
        filepath, buffer, index_column, start_timestamp, end_timestamp)
    columns_to_drop = [it for it in donnor.columns.drop(column_to_impute)]
    donnor.drop(columns=columns_to_drop, inplace=True)
    rows_to_drop = [it for it in donnor.index if it <
                    start_timestamp or it > end_timestamp]
    donnor.drop(rows_to_drop, inplace=True)
    return donnor


def hotdeck(df: pd.DataFrame, donnor: pd.DataFrame, gap_indices: [int], column_to_impute: str) -> pd.DataFrame:
    cp = df.copy()
    indices = donnor.index[:]
    i = 0

    for gap_idx in sorted(gap_indices):
        value = donnor[column_to_impute][donnor.index[-1]]
        for i in range(i, len(indices) - 1):
            if abs(indices[i + 1] - gap_idx) >= abs(indices[i] - gap_idx):
                value = donnor[column_to_impute][indices[i]]
                break
        cp[column_to_impute][gap_idx] = value
    return cp
