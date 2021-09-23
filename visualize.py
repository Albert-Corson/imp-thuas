#!/usr/bin/env python3

from matplotlib import pyplot as plt
from numpy.core.fromnumeric import resize
from Xlsx import Xlsx
from datetime import datetime


def linear_scatter(sheet_name, sheet):
    dates = []
    time_steps = []
    timestamps = sheet.index
    for idx in range(1, timestamps.size):
        time_steps.append((timestamps[idx] - timestamps[idx - 1]) / 60)
        dates.append(datetime.fromtimestamp(timestamps[idx]))
    plt.scatter(dates, time_steps, marker='.',
                s=2, alpha=0.8, label=sheet_name)


def scatter(sheet):
    time_steps = []
    timestamps = sheet.index
    for idx in range(1, timestamps.size):
        time_steps.append((timestamps[idx] - timestamps[idx - 1]) / 60)
    plt.scatter(range(0, len(time_steps)), time_steps, marker=',', s=1)
    plt.title("Time differences between data measurements")
    plt.xlabel("Timestamp number")
    plt.ylabel("Time steps (in minutes)")
    plt.show()


def scatter_houses(houses):
    plt.grid(True)

    for house in houses[18:]:
        plt.figure(figsize=(20, 10))

        plt.title(f"House {house}: time differences between data measurements")
        plt.xlabel("Date of measurement")
        plt.ylabel("Time steps in minutes")

        xls = Xlsx(f"./FactoryZero2019/{house}.xlsx")

        for sheet_name in xls.get_sheets_names()[:3]:
            linear_scatter(sheet_name, xls.get_sheet(sheet_name))

        plt.legend()
        plt.savefig(f"./visualizations/{house}.png", dpi=300)
        plt.close()


houses = [
    "054",
    "105",
    "114",
    "115",
    "056",
    "099",
    "037",
    "041",
    "051",
    "100",
    "058",
    "057",
    "055",
    "053",
    "040",
    "108",
    "021",
    "026",
    "091",
    "060"
]

scatter_houses(houses)
