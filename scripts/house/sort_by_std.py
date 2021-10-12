#!/usr/bin/env python3

import numpy as np
from os import path
import sys

DEPTH = "/../.."
ROOT = path.realpath(path.dirname(__file__) + DEPTH)
sys.path.append(ROOT)

from src.HouseXlsxIterator import HouseXlsxIterator  # noqa
from src.CSVDumper import CSVDumper  # noqa

result = []

for house_name, house in HouseXlsxIterator(f"{ROOT}/data/FactoryZero2019"):
    print(house_name)
    timesteps = []
    for sheet_name, sheet in house:
        for n in range(1, len(sheet.index)):
            timesteps.append(sheet.index[n] - sheet.index[n - 1])

    try:
        std = np.std(timesteps)
    except:
        std = -1

    result.append({
        "house": house_name,
        "std": std
    })

    result = sorted(
        result, key=lambda it: it["std"] if it["std"] != -1 else 100000000)

    CSVDumper.dump_array_of_dict(
        result, f"{ROOT}/data/house_sorting/scoreboard_by_std.csv")
