#!/usr/bin/env python3

from Xlsx import XlsxHouseFileIterator

result = {}

for house_name, house in XlsxHouseFileIterator():
    print(house_name)
    for sheet_name, sheet in house:
        if (sheet_name not in result):
            result[sheet_name] = []

        for field in sheet:
            if (field not in result[sheet_name]):
                result[sheet_name].append(field)

with open("sheet_fields.txt", "w+") as file:
    for key, value in result.items():
        print(key, '\n', ','.join(value), '\n\n',
              file=file, sep=None, end=None)
