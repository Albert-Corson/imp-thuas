from area import area
import numpy as np
import pandas as pd
import threading
import multiprocessing
from datetime import datetime
from scipy.spatial.distance import directed_hausdorff

from src.parse import parse_uploaded_file

cached_donors = dict()
cache_lock = threading.RLock()
gap_indices_lock = threading.RLock()
start_time = 0
total_gaps = 0


def hotdeck(receiver: pd.DataFrame, gap_indices: [int], donors: [str], index_col: str, sheet_name: str, column_to_impute: str) -> pd.DataFrame:
    global start_time, total_gaps

    # Init global variables
    total_gaps = len(gap_indices)
    start_time = datetime.now()

    print("Hotdeck starting, loading donors...")
    for file in donors:
        load_donor(file, index_col, column_to_impute, sheet_name)
    print(f"{len(donors)} donors loaded in {datetime.now() - start_time}")

    start_time = datetime.now()
    threads = []
    thread_count = multiprocessing.cpu_count() - 1
    receiver_cp = receiver.copy()
    gap_indices_cp = gap_indices.copy()

    print(f"Spawning {thread_count - 1} more threads...")
    for idx in range(thread_count - 1):
        threads.append(threading.Thread(
            target=impute,
            args=(receiver_cp, gap_indices_cp, donors, index_col, sheet_name, column_to_impute)
            ))
        threads[idx].start()

    impute(receiver_cp, gap_indices_cp, donors, index_col, sheet_name, column_to_impute)

    for thread in threads:
        thread.join()

    print(f"Time taken: {(datetime.now() - start_time)}")

    return receiver_cp


def get_normalized_dataframe(df: pd.DataFrame, start_time: int, end_time: int) -> pd.DataFrame:
    start_idx = df.index.get_loc(start_time if start_time >= df.index[0] else df.index[0], 'pad')
    view = df[df.index >= df.index[start_idx]]

    if end_time < view.index[-1]:
        end_idx = view.index.get_loc(end_time, 'bfill')
        view = view[view.index <= view.index[end_idx]]

    start_time_missing = view.index[0] != start_time
    end_time_missing = view.index[-1] != end_time

    cp = view.copy()

    if start_time_missing or end_time_missing:
        if start_time_missing:
            cp.loc[start_time] = [np.nan]
        if end_time_missing:
            cp.loc[end_time] = [np.nan]
        cp.sort_index(inplace=True)
        cp.interpolate(method="index", inplace=True)
        cp = cp[cp.index >= start_time]
        cp = cp[cp.index <= end_time]

    return cp


def load_donor(filepath: str, index_column: str, column_to_impute: str, sheet_name: str = None, start_time: int = None, end_time: int = None) -> None:
    global cached_donors, cache_lock

    with cache_lock:
        if filepath not in cached_donors.keys():
            with open(filepath, 'rb') as file:
                cached_donors[filepath] = parse_uploaded_file(filepath, file.read(), index_column, column_to_impute, sheet_name)
    donor = cached_donors[filepath].copy()
    if start_time != None:
        donor = donor[donor.index >= start_time]
    if end_time != None:
        donor = donor[donor.index <= end_time]
    return donor


def transpose_data(donor: str, receiver: str, gap_indices: [int], column_to_impute: str) -> None:
    for gap_idx in gap_indices:
        if gap_idx not in donor.index:
            donor.loc[gap_idx] = [np.nan]

    donor.sort_index(inplace=True)
    donor.interpolate(method="index", inplace=True)

    for gap_idx in gap_indices:
        receiver[column_to_impute][gap_idx] = donor[column_to_impute][gap_idx]


def get_gap_boundaries(df: pd.DataFrame, gap_start_time: int, gap_end_time: int) -> tuple:
    gap_start_idx = df.index.get_loc(gap_start_time) - 1
    gap_end_idx = df.index.get_loc(gap_end_time) + 1

    if gap_start_idx < 0:
        gap_start_idx = 0
    if gap_end_idx >= len(df):
        gap_end_idx = len(df) - 1

    return gap_start_idx, gap_end_idx


def pop_gap(gap_indices: [[int]]) -> [int]:
    global gap_indices_lock

    with gap_indices_lock:
        gaps_left = len(gap_indices)
        if gaps_left > 0:
            return gap_indices.pop(0)
    return None


def fill_gap(receiver: pd.DataFrame, gap: [int], gap_start_time:int, gap_end_time: int, scoreboard: [dict], index_col: str, column_to_impute: str, sheet_name: str) -> None:
    if len(scoreboard) != 0:
        scoreboard.sort(key=lambda it: it["score"])
        best = scoreboard[0]
        donor = load_donor(best["filename"], index_col, column_to_impute, sheet_name, best["start"], best["end"])
        donor.index = donor.index + best["x_offset"]
        donor[column_to_impute] = donor[column_to_impute] - best["y_offset"]
    else:
        donor = pd.DataFrame({
            column_to_impute: [
                receiver[column_to_impute][gap_start_time],
                receiver[column_to_impute][gap_end_time]
            ]},
            index=[gap_start_time, gap_end_time]
        )

    transpose_data(donor, receiver, gap, column_to_impute)


def impute(receiver: pd.DataFrame, gap_indices: [[int]], donors: [str], index_col: str, sheet_name: str, column_to_impute: str) -> None:
    while (gap := pop_gap(gap_indices)) != None:
        print_progress(len(gap_indices))

        gap_start_idx, gap_end_idx = get_gap_boundaries(receiver, gap[0], gap[-1])
        gap_start_time = receiver.index[gap_start_idx]
        gap_end_time = receiver.index[gap_end_idx]

        duration_before, duration_after = get_sampling_durations(receiver, column_to_impute, gap_start_idx, gap_end_idx, gap_start_time, gap_end_time)

        before = get_normalized_dataframe(receiver, gap_start_time - duration_before, gap_start_time)
        after = get_normalized_dataframe(receiver, gap_end_time, gap_end_time + duration_after)

        donor_start_time = gap_start_time - (duration_before + 3600)
        donor_end_time = gap_end_time + (duration_after + 3600)

        scoreboard = []

        for file in donors:
            donor = load_donor(file, index_col, column_to_impute, sheet_name, donor_start_time, donor_end_time)
            scoreboard += scan_donor(before, after, file, donor, column_to_impute)

        fill_gap(receiver, gap, gap_start_time, gap_end_time, scoreboard, index_col, column_to_impute, sheet_name)


def scan_donor(before: pd.DataFrame, after: pd.DataFrame, donor_filename: str, donor: pd.DataFrame, column_to_impute: str) -> [dict]:
    scores = []
    step = 300

    original_sample_mean = (before[column_to_impute].mean() + after[column_to_impute].mean()) / 2

    # Shift the comparison sample the start of the donor sample
    x_offset = before.index[0] - donor.index[0]
    x_offset -= x_offset % step
    before.index = before.index - x_offset
    after.index = after.index - x_offset

    while after.index[-1] <= donor.index[-1]:
        # Donor comparison samples
        donor_before = get_normalized_dataframe(donor, before.index[0], before.index[-1])
        donor_after = get_normalized_dataframe(donor, after.index[0], after.index[-1])

        # We need to take into account the previous Y-axis shifting
        y_offset, adjusted_y_offset = get_y_offsets(original_sample_mean, before, after, donor_before, donor_after, column_to_impute)

        # Apply the offset
        before[column_to_impute] = before[column_to_impute] + adjusted_y_offset
        after[column_to_impute] = after[column_to_impute] + adjusted_y_offset

        scores.append({
            "score": get_similarity_score(before, after, donor_before, donor_after, column_to_impute),
            "x_offset": x_offset,
            "y_offset": y_offset,
            "start": before.index[0],
            "end": after.index[-1],
            "filename": donor_filename
        })

        # Shift the comparison sample to the next step
        x_offset -= step
        before.index = before.index + step
        after.index = after.index + step

    return scores


def get_sampling_durations(receiver: pd.DataFrame, col_to_impute: str, gap_start_idx: int, gap_end_idx: int, gap_start_time: int, gap_end_time: int) -> tuple:
    gap_duration = gap_end_time - gap_start_time
    max_duration = gap_duration * 1.5 if gap_duration > 1800 else 1800
    index_count = len(receiver.index)

    duration_before = 0
    while gap_start_idx > 0 \
            and duration_before < max_duration \
            and np.isnan(receiver[col_to_impute][receiver.index[gap_start_idx]]) == False:
        duration_before = gap_start_time - receiver.index[gap_start_idx]
        gap_start_idx -= 1

    duration_after = 0
    while gap_end_idx < index_count \
            and duration_after < max_duration \
            and np.isnan(receiver[col_to_impute][receiver.index[gap_end_idx]]) == False:
        duration_after = receiver.index[gap_end_idx] - gap_end_time
        gap_end_idx += 1

    return duration_before, duration_after


def get_area(before: pd.DataFrame, after: pd.DataFrame, donor_before: pd.DataFrame, donor_after: pd.DataFrame, column_to_impute: str) -> float:
    area1 = get_sub_area(before, donor_before, column_to_impute)
    if f"{area1}" == "nan":
        area1 = get_sub_area(donor_before, before, column_to_impute)

    area2 = get_sub_area(after, donor_after, column_to_impute)
    if f"{area2}" == "nan":
        area2 = get_sub_area(donor_after, after, column_to_impute)

    return area1 + area2


def get_sub_area(first, second, column_to_impute):
    points = []

    for timestamp in first.index:
        points.append([timestamp, first[column_to_impute][timestamp]])
    for idx in range(len(second.index) - 1, 0, -1):
        points.append([second.index[idx], second[column_to_impute][second.index[idx]]])

    return area({'type': 'Polygon', 'coordinates': [points]})


def get_y_offsets(original_sample_mean, before, after, donor_before, donor_after, column_to_impute) -> tuple:
    mean_receiver = (before[column_to_impute].mean() + after[column_to_impute].mean()) / 2
    mean_donor = (donor_before[column_to_impute].mean() + donor_after[column_to_impute].mean()) / 2
    adjusted_y_offset = mean_donor - mean_receiver
    y_offset = adjusted_y_offset - (original_sample_mean - mean_receiver)
    return y_offset, adjusted_y_offset


def get_similarity_score(before: pd.DataFrame, after: pd.DataFrame, donor_before: pd.DataFrame, donor_after: pd.DataFrame, column_to_impute: str) -> float:
    return max([
            directed_hausdorff(before, donor_before)[0] + directed_hausdorff(after, donor_after)[0],
            directed_hausdorff(donor_before, before)[0] + directed_hausdorff(donor_after, after)[0]
        ])


def print_progress(gaps_left: int) -> None:
    global start_time, total_gaps

    if threading.current_thread() is threading.main_thread():
        elapsed = datetime.now() - start_time
        total_time_estimate = (elapsed / (total_gaps - gaps_left + 1)) * total_gaps
        eta = total_time_estimate - elapsed
        progress = 100 - ((gaps_left / total_gaps) * 100)
        print(f"{total_gaps - gaps_left}/{total_gaps}\tElapsed: {elapsed}\tETA: {eta}\tProgress :" + "%.2f%%" % progress)
