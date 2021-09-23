#!/usr/bin/env python3

from numpy import invert
import pandas as pd

# files = [
#     "./csv/by_sheets/alklimaHeatPump.csv",
#     "./csv/by_sheets/co2sensor.csv",
#     "./csv/by_sheets/energyBooster.csv",
#     "./csv/by_sheets/energyHeatpump.csv",
#     "./csv/by_sheets/energyImmersion.csv",
#     "./csv/by_sheets/energyWtwReg.csv",
#     "./csv/by_sheets/flowHeatSpaceHeating.csv",
#     "./csv/by_sheets/immersion.csv",
#     "./csv/by_sheets/relay1.csv",
#     "./csv/by_sheets/relay24v.csv",
#     "./csv/by_sheets/relay2.csv",
#     "./csv/by_sheets/smartMeter.csv",
#     "./csv/by_sheets/solar.csv",
#     "./csv/by_sheets/thermostat.csv",
#     "./csv/by_sheets/ventilation.csv",
#     "./csv/by_sheets/waterFlow.csv"
# ]

# result = dict()

# for path in files:
#     csv = pd.read_csv(path, index_col="house")

#     lines = len(csv.index)
#     for n in range(0, lines):
#         house = csv.index[n]
#         if house not in result:
#             result[house] = 0
#         result[house] = result[house] + lines - n + 1

# result = {k: v for k, v in sorted(result.items(), key=lambda v: v[1], reverse=True)}

# print("house,score")
# for k, v in result.items():
#     print("%03d,%d" % (k, v))

csv = pd.read_csv("csv/sorted.csv", index_col="House number")

result = []

for idx in csv.index:
    result.append({
        "house": "%03d" % idx,
        "average_timestep": csv["Average per page"][idx],
        "total_timestep": csv["Total time difference"][idx],
        "pages": csv["Number of pages"][idx]
    })

result = sorted(result, key=lambda it: it["average_timestep"])

print(','.join(result[0].keys()))
for it in result:
    print(','.join(str(x) for x in it.values()))
