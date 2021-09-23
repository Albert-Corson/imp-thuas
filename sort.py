from datetime import date
import pandas as pd
import numpy as np
from Xlsx import Xlsx
import sys


def get_time_difference_total(sheet):
    total = 0
    for i in range(1, len(sheet.index)):
        total += sheet.index[i] - sheet.index[i - 1]
    return total


result = []

for i in range(1, 121):
    house = "%03d" % i
    print("Processing %s" % house)

    total = 0
    xls = Xlsx("./FactoryZero2019/%s.xlsx" % house)
    names = xls.get_sheets_names()
    names_len = len(names)
    for n in range(0, names_len):
        print(f"{n + 1}/{names_len}")
        sheet = xls.get_sheet(names[n])
        total += get_time_difference_total(sheet)
    result.append({
        "house": house,
        "total": total,
        "average": total / names_len,
        "pages": names_len
    })

with open("sorted.csv", "w+") as file:
    sys.stdout = file
    print("House number, Total time difference, Average per page, Number of pages")
    for it in result:
        print(f"{it['house']}, {it['total']}, {it['average']}, {it['pages']}")
