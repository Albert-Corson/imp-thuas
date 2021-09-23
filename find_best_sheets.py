#!/usr/bin/env python3

from datetime import time
import numpy as np
from Xlsx import Xlsx
import sys


def save_result(result):
    print("Saving...")
    for key, value in result.items():
        with open(f"./csv/by_sheets/{key}.csv", "w+") as file:
            stdout = sys.stdout
            sys.stdout = file
            print(','.join(value[0].keys()))
            for entry in value:
                print(','.join(str(x) for x in entry.values()))
            sys.stdout = stdout


def sort_result(result):
    print("Sorting...")
    sorted_result = dict()
    for key, value in result.items():
        sorted_result[key] = sorted(value, key=lambda it: it["std"])
    return sorted_result


def process_sheet(xls, sheet_name):
    sheet = xls.get_sheet(sheet_name)

    time_steps = []
    timestamps = sheet.index
    for idx in range(1, timestamps.size):
        time_steps.append((timestamps[idx] - timestamps[idx - 1]) / 60)

    try:
        std = np.std(time_steps)
    except:
        std = -1

    return {
        "std": std,
        "indexes": timestamps.size,
    }


def process_house(house_number, output):
    house_name = "%03d" % house_number
    print(f"Processing {house_name}")

    xls = Xlsx(f"./FactoryZero2019/{house_name}.xlsx")

    sheet_names = xls.get_sheets_names()
    names_len = len(sheet_names)

    for idx in range(0, names_len):
        sheet_name = sheet_names[idx]
        print(f"{idx + 1}/{names_len} {sheet_name}")
        sheet_result = process_sheet(xls, sheet_name)

        sheet_result["house"] = house_name

        if sheet_name not in output:
            output[sheet_name] = []

        output[sheet_name].append(sheet_result)


def process():
    result = dict()
    for house_num in range(1, 121):
        process_house(house_num, result)
        save_result(sort_result(result))

    return result


process()
