from datetime import datetime
import numpy as np
import pandas as pd
import random

from src.evaluation import evaluate
from src.hotdeck import hotdeck
from src.parse import parse_uploaded_file
from src.plot import plot_imputation, show_all_plots

filepath = "data/FactoryZero2019/054.xlsx"
index_column = "Timestamp"
sheet_name = "smartMeter"  # For Excel files only
column_to_impute = "power"
start_timestamp = 1549196400
end_timestamp = 1562281477
donors = ["data/FactoryZero2019/054.xlsx"]
show_plots = True

# Define types of gaps we want to create: each row defines a type:
# [min gap sizes, max gap size, gaps ratio]
gaps_config = [
    [1,  6,   0.075],
    [6,  24,  0.05],
    [24, 72,  0.015],
    [72, 168, 0.005]
]

df: pd.DataFrame = None
dfs_with_gaps: [pd.DataFrame] = []
imputed_dfs: [pd.DataFrame] = []
gaps_indices = []


# TODO: this doesn't seem to work properly for functions other than random()
random.seed(7094400398089273)


def create_gaps(df: pd.DataFrame, gaps_ratio: float, min_gap_size: int, max_gap_size: int):
    min_gap_distance = 5
    indices_to_remove: [int] = []
    df_with_gaps = df.copy()
    gaps_locations = sorted(random.sample(range(1, len(df) + 1), int(len(df) * gaps_ratio)))

    for i, gap_start in enumerate(gaps_locations):
        gap_end = min(gap_start + random.randrange(min_gap_size, max_gap_size), len(df) - 1)

        if len(gaps_locations) >= i + 2 and gap_end + min_gap_distance >= gaps_locations[i + 1]:
            # gaps are too close to each other -> ignore
            continue

        indices_to_remove.append([df.index[i] for i in range(gap_start, gap_end)])
        df_with_gaps.loc[indices_to_remove[-1]] = [np.nan]

    return df_with_gaps, indices_to_remove


print("Starting...")
try:
    with open(filepath, 'rb') as file:
        buffer = file.read()
except:
    print("File not found")
    exit()

print("Parsing file...")
df = parse_uploaded_file(
    filepath, buffer, index_column, column_to_impute, sheet_name, start_timestamp, end_timestamp)


print("Creating gaps...")
for i in range(len(gaps_config)):
    min_gap_size, max_gap_size, gaps_ratio = gaps_config[i]
    gapped_df, indices = create_gaps(
        df, gaps_ratio, min_gap_size, max_gap_size)
    dfs_with_gaps.append(gapped_df)
    gaps_indices.append(indices)


print("Imputing...")
for i in range(len(dfs_with_gaps)):
    imputed_dfs.append(hotdeck(dfs_with_gaps[i], gaps_indices[i], donors, index_column, sheet_name, column_to_impute))


print("Evaluating...")
evaluate(df, imputed_dfs, gaps_config, gaps_indices, show_plots)


if show_plots:
    print("Ploting imputation...")
    df.index = [datetime.fromtimestamp(it) for it in df.index]
    for i in range(len(imputed_dfs)):
        dfs_with_gaps[i].index = [datetime.fromtimestamp(it) for it in dfs_with_gaps[i].index]
        imputed_dfs[i].index = [datetime.fromtimestamp(it) for it in imputed_dfs[i].index]
        plot_imputation(df, dfs_with_gaps[i], imputed_dfs[i],
                        column_to_impute, f"Interpolation with gap type {i + 1} [{gaps_config[i][0]};{gaps_config[i][1]}]")
    show_all_plots()
