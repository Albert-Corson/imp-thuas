#!/usr/bin/env python3

from os import makedirs, path
import sys

DEPTH = "/../.."
ROOT = path.realpath(path.dirname(__file__) + DEPTH)
sys.path.append(ROOT)

from src.HouseXlsxIterator import HouseXlsxIterator  # noqa

result = {}

for house_name, xlsx in HouseXlsxIterator(f"{ROOT}/data/FactoryZero2019"):
    print(house_name)
    for sheet_name, sheet in xlsx:
        if (sheet_name not in result):
            result[sheet_name] = []

        for field in sheet:
            if (field not in result[sheet_name]):
                result[sheet_name].append(field)

makedirs(f"{ROOT}/output/houses/", exist_ok=True)

with open(f"{ROOT}/output/houses/sheet_columns_name.txt", "w+") as file:
    for key, value in result.items():
        print(key, '\n', ','.join(value), '\n\n',
              file=file, sep=None, end=None)
