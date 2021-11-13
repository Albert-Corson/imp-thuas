from datetime import datetime
import numpy as np
import pandas as pd
from parse import parse_uploaded_file
import matplotlib.pyplot as plt
from scipy.spatial.distance import directed_hausdorff
import threading

start_time = None
max_thread_count = 7
fifteen_days = 1339200
cached_donors = dict()
cache_lock = threading.RLock()
gap_indices_lock = threading.RLock()
df_lock = threading.RLock()
total_gaps = None
df_len = None


def hotdeck(df: pd.DataFrame, gaps_indices: [int], donors: [str], index_col: str, sheet_name: str, column_to_impute: str):
    global df_len, total_gaps, max_thread_count, start_time

    threads = []
    total_gaps = len(gaps_indices)
    df_len = len(df)

    gaps = gaps_indices[:]
    start_time = datetime.now()

    for idx in range(max_thread_count):
        threads.append(threading.Thread(
            target=impute_gaps,
            args=(df, gaps, donors, index_col, sheet_name, column_to_impute)
            ))
        threads[idx].start()

    for thread in threads:
        thread.join()


def impute_gaps(df: pd.DataFrame, gaps_indices: [int], donors: [str], index_col: str, sheet_name: str, column_to_impute: str):
    global fifteen_days, df_len, total_gaps, max_thread_count, df_lock, gap_indices_lock, start_time

    gaps_left = len(gaps_indices)

    while gaps_left != 0:
        elapsed = datetime.now() - start_time
        total_time_estimate = (elapsed / (total_gaps - gaps_left + 1)) * total_gaps
        eta = total_time_estimate - elapsed

        progress = 100 - ((len(gaps_indices) / total_gaps) * 100)

        print(f"ETA: {eta}\tProgress :" + "%.2f%%" % progress)

        with gap_indices_lock:
            gap = gaps_indices.pop(0)

        gap_start_idx, gap_end_idx = get_gap_boundaries(df, df_len, gap[0], gap[-1])
        gap_start_timestamp = df.index[gap_start_idx]
        gap_end_timestamp = df.index[gap_end_idx]
        gap_size = gap_end_timestamp - gap_start_timestamp
        surrounding_size = gap_size * 1.5 if gap_size > 1800 else 1800

        before_gap = get_normalized_dataframe(df, gap_start_timestamp - surrounding_size, gap_start_timestamp)
        after_gap = get_normalized_dataframe(df, gap_end_timestamp, gap_end_timestamp + surrounding_size)

        donor_start = gap_start_timestamp - (fifteen_days / 30)
        donor_end = gap_end_timestamp + (fifteen_days / 30)

        scoreboard = []

        for file in donors:
            donor = load_donor(file, index_col, column_to_impute, sheet_name, donor_start, donor_end)
            scoreboard += scan_donor(before_gap, after_gap, file, donor, column_to_impute)

        scoreboard.sort(key=lambda it: it["score"])

        transpose_data(scoreboard[0], df, gap, index_col, column_to_impute, sheet_name)

        gaps_left = len(gaps_indices)


def scan_donor(before_gap: pd.DataFrame, after_gap: pd.DataFrame, donor_name: str, donor: pd.DataFrame, column_to_impute: str) -> [dict]:
    scores = []
    step = 300

    offsetX = before_gap.index[0] - donor.index[0]
    before_gap.index = before_gap.index - offsetX
    after_gap.index = after_gap.index - offsetX

    while after_gap.index[-1] <= donor.index[-1]:
        donor_before = get_normalized_dataframe(donor, before_gap.index[0], before_gap.index[-1])
        donor_after = get_normalized_dataframe(donor, after_gap.index[0], after_gap.index[-1])

        mean_diff_before = donor_before[column_to_impute].mean() - before_gap[column_to_impute].mean()
        mean_diff_after = donor_after[column_to_impute].mean() - after_gap[column_to_impute].mean()
        offsetY = (mean_diff_before + mean_diff_after) / 2

        before_gap[column_to_impute] = before_gap[column_to_impute] + offsetY
        after_gap[column_to_impute] = after_gap[column_to_impute] + offsetY

        dh1 = directed_hausdorff(before_gap, donor_before)
        dh2 = directed_hausdorff(after_gap, donor_after)

        scores.append({
            "score": (dh1[0] + dh2[0]) * (1 + dh1[1] + dh2[1] + dh1[2] + dh2[2]),
            "donor": donor_name,
            "offsetY": offsetY,
            "offsetX": offsetX,
            "start": before_gap.index[0],
            "end": after_gap.index[-1]
        })

        # Continue
        offsetX -= step
        before_gap.index = before_gap.index + step
        after_gap.index = after_gap.index + step

    return scores


def load_donor(filepath: str, index_column: str, column_to_impute: str, sheet_name: str = None, start_timestamp: int = None, end_timestamp: int = None):
    global cached_donors, cache_lock

    with cache_lock:
        if filepath not in cached_donors.keys():
            with open(filepath, 'rb') as file:
                buffer = file.read()
                cached_donors[filepath] = parse_uploaded_file(filepath, buffer, index_column, column_to_impute, sheet_name)

    df = cached_donors[filepath].copy()

    if start_timestamp != None:
        df = df[df.index >= start_timestamp]
    if end_timestamp != None:
        df = df[df.index <= end_timestamp]

    return df


def get_normalized_dataframe(df: pd.DataFrame, start_timestamp: int, end_timestamp: int) -> pd.DataFrame:
    start_idx = df.index.get_loc(start_timestamp if start_timestamp >= df.index[0] else df.index[0], 'pad')
    end_idx = df.index.get_loc(end_timestamp if end_timestamp <= df.index[-1] else df.index[-1], 'backfill')

    cp = df[df.index >= df.index[start_idx]]
    cp = cp[cp.index <= df.index[end_idx]]

    if cp.index[0] != start_timestamp:
        cp.loc[start_timestamp] = [np.nan]
    if cp.index[-1] != end_timestamp:
        cp.loc[end_timestamp] = [np.nan]

    cp.sort_index(inplace=True)
    cp.interpolate(inplace=True)

    cp = cp[cp.index >= start_timestamp]
    return cp[cp.index <= end_timestamp]


def transpose_data(best_donor: dict, df: pd.DataFrame, gap_indices: [int], index_col: str, column_to_impute: str, sheet_name: str):
    global df_lock

    donor = load_donor(best_donor["donor"], index_col, column_to_impute, sheet_name, best_donor["start"], best_donor["end"])
    donor.index = donor.index + best_donor["offsetX"]
    donor[column_to_impute] = donor[column_to_impute] - best_donor["offsetY"]

    for gap_idx in gap_indices:
        donor.loc[gap_idx] = [np.nan]

    donor.sort_index(inplace=True)
    donor.interpolate(inplace=True)

    with df_lock:
        for gap_idx in gap_indices:
            df[column_to_impute][gap_idx] = donor[column_to_impute][gap_idx]


def get_gap_boundaries(df: pd.DataFrame, df_len: int, gap_start_timestamp: int, gap_end_timestamp: int) -> tuple:
    gap_start_idx = df.index.get_loc(gap_start_timestamp) - 1
    gap_end_idx = df.index.get_loc(gap_end_timestamp) + 1

    if gap_start_idx < 0:
        gap_start_idx = 0
    if gap_end_idx >= df_len:
        gap_end_idx = df_len - 1

    return gap_start_idx, gap_end_idx
