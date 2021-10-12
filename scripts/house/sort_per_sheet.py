#!/usr/bin/env python3

import numpy as np
from os import path
import sys

DEPTH = "/../.."
ROOT = path.realpath(path.dirname(__file__) + DEPTH)
sys.path.append(ROOT)

from src.CSVDumper import CSVDumper  # noqa
from src.HouseXlsxIterator import HouseXlsxIterator  # noqa


def sort_by_std(result):
    for key, value in result.items():
        result[key] = sorted(value, key=lambda it: it["std"])


def process_sheet(house_name, sheet):
    timesteps = []
    timestamps = sheet.index
    for idx in range(1, timestamps.size):
        timesteps.append((timestamps[idx] - timestamps[idx - 1]) / 60)

    try:
        std = np.std(timesteps)
    except:
        std = -1

    return {
        "house": house_name,
        "std": std,
        "indexes": timestamps.size,
    }


result = dict()

for house_name, xlsx in HouseXlsxIterator(f"{ROOT}/data/FactoryZero2019"):
    print(f"Processing {house_name}...")
    for sheet_name, sheet in xlsx:
        print(f"  Sheet {sheet_name}...")
        sheet_result = process_sheet(house_name, sheet)
        if sheet_name not in result:
            result[sheet_name] = []

    print("Sorting and saving...")
    sort_by_std(result)
    CSVDumper.dump_dict_in_files(
        result, f"{ROOT}/data/house_sorting/per_sheet")
