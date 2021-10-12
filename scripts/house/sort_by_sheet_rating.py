#!/usr/bin/env python3

import pandas as pd
from os import path
import sys

DEPTH = "/../.."
ROOT = path.realpath(path.dirname(__file__) + DEPTH)
sys.path.append(ROOT)

from src.CSVDumper import CSVDumper  # noqa

files = [
    "data/house_sorting/per_sheet/alklimaHeatPump.csv",
    "data/house_sorting/per_sheet/co2sensor.csv",
    "data/house_sorting/per_sheet/energyBooster.csv",
    "data/house_sorting/per_sheet/energyHeatpump.csv",
    "data/house_sorting/per_sheet/energyImmersion.csv",
    "data/house_sorting/per_sheet/energyWtwReg.csv",
    "data/house_sorting/per_sheet/flowHeatSpaceHeating.csv",
    "data/house_sorting/per_sheet/immersion.csv",
    "data/house_sorting/per_sheet/relay1.csv",
    "data/house_sorting/per_sheet/relay24v.csv",
    "data/house_sorting/per_sheet/relay2.csv",
    "data/house_sorting/per_sheet/smartMeter.csv",
    "data/house_sorting/per_sheet/solar.csv",
    "data/house_sorting/per_sheet/thermostat.csv",
    "data/house_sorting/per_sheet/ventilation.csv",
    "data/house_sorting/per_sheet/waterFlow.csv"
]

result = dict()

for path in files:
    csv = pd.read_csv(f"{ROOT}/{path}", index_col="house")

    lines = len(csv.index)
    for n in range(0, lines):
        house = csv.index[n]
        if house not in result:
            result[house] = 0
        result[house] = result[house] + lines - n + 1

result = {k: v for k, v in sorted(
    result.items(), key=lambda v: v[1], reverse=True)}

CSVDumper.dump_dict(result, ["house", "score"],
                    f"{ROOT}/data/house_sorting/scoreboard_by_sheet_rating.csv")
