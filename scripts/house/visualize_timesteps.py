#!/usr/bin/env python3

from datetime import datetime
from matplotlib import pyplot as plt
from os import makedirs, path
import sys

DEPTH = "/../.."
ROOT = path.realpath(path.dirname(__file__) + DEPTH)
sys.path.append(ROOT)

from src.HouseXlsxIterator import HouseXlsxIterator  # noqa


def linear_scatter(sheet_name, sheet):
    dates = []
    timesteps = []
    timestamps = sheet.index
    for idx in range(1, timestamps.size):
        timesteps.append((timestamps[idx] - timestamps[idx - 1]) / 60)
        dates.append(datetime.fromtimestamp(timestamps[idx]))
    plt.scatter(dates, timesteps, marker='.',
                s=2, alpha=0.8, label=sheet_name)


makedirs(f"{ROOT}/output/houses/timesteps/", exist_ok=True)

for house_name, xlsx in HouseXlsxIterator(f"{ROOT}/data/FactoryZero2019"):
    print(f"Processing {house_name}...")

    plt.grid(True)
    plt.figure(figsize=(20, 10))
    plt.title(
        f"House {house_name}: time differences between data measurements")
    plt.xlabel("Date of measurement")
    plt.ylabel("Time steps in minutes")

    for sheet_name, sheet in xlsx:
        print(f"  Sheet {sheet_name}...")
        linear_scatter(sheet_name, sheet)

    plt.legend()
    plt.savefig(f"{ROOT}/output/houses/timesteps/{house_name}.png", dpi=300)
    plt.close()
