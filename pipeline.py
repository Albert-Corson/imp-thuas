import numpy as np
import pandas as pd
import random

from evaluation import evaluate
from hotdeck import hotdeck, load_donnor
from parse import parse_uploaded_file
from plot import plot_imputation, show_all_plots
from interpolate import interpolate

filepath = "data/FactoryZero2019/054.xlsx"
index_column = "Timestamp"
sheet_name = "smartMeter"  # For Excel files only
column_to_impute = "power"
start_timestamp = 1549196400
end_timestamp = 1562281477
donnor = "data/FactoryZero2019/099.xlsx"
show_plots = True

# Define types of gaps we want to create: each row defines a type:
# [min gap sizes, max gap size, gaps ratio]
gaps_config = [
    [1,  6,   0.15],
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
    indices_to_remove: [int] = []
    gaps_locations = sorted(random.sample(
        range(1, len(df) + 1), int(len(df) * gaps_ratio)))

    for gap_start in gaps_locations:
        # TODO: remove gaps too close to each other
        gap_end = min(gap_start + random.randrange(min_gap_size,
                      max_gap_size), len(df) - 1)
        indices_to_remove += [df.index[i] for i in range(gap_start, gap_end)]
    df_with_gaps = df.copy()
    df_with_gaps.loc[indices_to_remove, :] = np.nan
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
    filepath, buffer, index_column, column_to_impute, start_timestamp, end_timestamp, sheet_name)


print("Creating gaps...")
for i in range(len(gaps_config)):
    min_gap_size, max_gap_size, gaps_ratio = gaps_config[i]
    gapped_df, indices = create_gaps(
        df, gaps_ratio, min_gap_size, max_gap_size)
    dfs_with_gaps.append(gapped_df)
    gaps_indices.append(indices)


donnor = load_donnor(donnor, index_column,
                     column_to_impute, start_timestamp, end_timestamp, sheet_name)

print("Imputing...")
for i in range(len(dfs_with_gaps)):
    imputed_dfs.append(
        hotdeck(dfs_with_gaps[i], donnor, gaps_indices[i], column_to_impute))
    # imputed_dfs.append(interpolate(dfs_with_gaps[i]))


print("Evaluating...")
evaluate(df, imputed_dfs, gaps_config, gaps_indices, show_plots)


if show_plots:
    print("Ploting imputation...")
    for i in range(len(imputed_dfs)):
        plot_imputation(df, dfs_with_gaps[i], imputed_dfs[i],
                        column_to_impute, f"Interpolation with gap type {i + 1} [{gaps_config[i][0]};{gaps_config[i][1]}]")
    show_all_plots()
