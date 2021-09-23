#!/usr/bin/env python3

import pandas as pd

csv = pd.read_csv("./sorted.csv", index_col="House number")

items = csv["Average per page"].items()

houses = {k: v for k, v in sorted(items, key=lambda item: item[1])}

print("House number,Average per page")
for key, value in houses.items():
    print(f"{key},{int(value)}")
