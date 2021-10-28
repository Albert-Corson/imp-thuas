import numpy as np
import io
import pandas as pd
import os
import random

from date_parsers import custom_knmi_date_parser, date_parser, factoryzero_date_parser, knmi_date_parser
from evaluation import abs_raw_bias, error_variance, evaluate, max_error, mean_squared_error, percent_bias, raw_bias, sum_error
from plot import plot_imputation, show_all_plots

filepath = "data/FactoryZero2019/054.xlsx"
index_column = "Timestamp"
sheet_name = "smartMeter"  # For Excel files only
column_to_impute = "power"
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


def parse_csv(buffer: bytes, index_column: str, separator: str = ',') -> pd.DataFrame:
    data = io.StringIO(buffer.decode('utf-8'))
    return pd.read_csv(data, sep=separator, index_col=index_column,
                     converters={index_column: date_parser})


def parse_xlsx(buffer: bytes, index_column: str) -> pd.DataFrame:
    df = pd.read_excel(buffer, sheet_name=sheet_name, index_col=index_column,
                       converters={index_column: factoryzero_date_parser})
    df.drop(columns=[it for it in df.columns.drop(
        column_to_impute)], inplace=True)
    return df


def parse_uploaded_file(filename: str, buffer: bytes, index_column: str) -> pd.DataFrame:
    ext = os.path.splitext(filename)[1][1:]
    if ext == 'csv':
        return parse_csv(buffer, index_column)
    elif ext == 'xlsx':
        return parse_xlsx(buffer, index_column)
    else:
        raise Exception(f'Unsupported file extension: {ext}')


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


def interpolate(df: pd.DataFrame) -> pd.DataFrame:
    cp = df.copy()
    indices = cp.index
    cp.index = [pd.to_datetime(it) for it in cp.index]
    cp.interpolate('time', inplace=True)
    cp.index = indices
    return cp


print("Starting...")
try:
    with open(filepath, 'rb') as file:
        buffer = file.read()
except:
    print("File not found")
    exit()

try:
    df = parse_uploaded_file(filepath, buffer, index_column)
    print("File parsed")
except:
    print("Invalid file format")
    exit()


print("Creating gaps...")
for i in range(len(gaps_config)):
    min_gap_size, max_gap_size, gaps_ratio = gaps_config[i]
    gapped_df, indices = create_gaps(df, gaps_ratio, min_gap_size, max_gap_size)
    dfs_with_gaps.append(gapped_df)
    gaps_indices.append(indices)


print("Imputing...")
for i in range(len(dfs_with_gaps)):
    imputed_dfs.append(interpolate(dfs_with_gaps[i]))


print("Evaluating...")
evaluate(df, imputed_dfs, gaps_config, gaps_indices, show_plots)


if show_plots:
    print("Ploting imputation...")
    for i in range(len(imputed_dfs)):
        plot_imputation(df, dfs_with_gaps[i], imputed_dfs[i],
                        "Temperature", f"Interpolation with gap type {i + 1} [{gaps_config[i][0]};{gaps_config[i][1]}]")
    show_all_plots()
