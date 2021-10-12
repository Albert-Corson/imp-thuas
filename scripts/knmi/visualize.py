#!/usr/bin/env python3

from os import path, makedirs
from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime

DEPTH = "/../.."
ROOT = path.realpath(path.dirname(__file__) + DEPTH)


def get_dates(csv):
    dates = []
    for idx in csv.index:
        date = str(csv["Date(YYYYMMDD)"][idx])
        hour = csv["Hour"][idx] - 1
        dates.append(
            datetime(int(date[:4]), int(date[4:6]),
                     int(date[6:8]), hour)
        )
    return dates


csv = pd.read_csv(f"{ROOT}/data/cleanKNMIdata.csv")
dates = get_dates(csv)

makedirs(f"{ROOT}/output/knmi/", exist_ok=True)

for col in csv:
    plt.figure(figsize=(20, 10))
    plt.title(col)
    plt.scatter(dates, csv[col], marker='.',
                s=2, alpha=0.8)
    plt.savefig(f"{ROOT}/output/knmi/{col}.png", dpi=300)
    plt.close()
