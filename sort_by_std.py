#!/usr/bin/env python3

from dump_csv import dump_csv
from Xlsx import XlsxHouseFileIterator
import numpy as np

result = []

for house_name, house in XlsxHouseFileIterator():
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

    result = sorted(result, key=lambda it: it["std"] if it["std"] != -1 else 100000000)

    dump_csv("./csv/house_by_overrall_std.csv", result)
