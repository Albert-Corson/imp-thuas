import pandas as pd
import threading

lock = threading.RLock()
other_lock = threading.RLock()

houses = [
    "data/FactoryZero2019/054.xlsx",
    "data/FactoryZero2019/099.xlsx",
    "data/FactoryZero2019/058.xlsx",
    "data/FactoryZero2019/100.xlsx",
    "data/FactoryZero2019/115.xlsx",
    "data/FactoryZero2019/039.xlsx",
    "data/FactoryZero2019/105.xlsx",
    "data/FactoryZero2019/056.xlsx",
    "data/FactoryZero2019/037.xlsx",
    "data/FactoryZero2019/055.xlsx",
    "data/FactoryZero2019/051.xlsx",
    "data/FactoryZero2019/041.xlsx",
    "data/FactoryZero2019/057.xlsx",
    "data/FactoryZero2019/040.xlsx",
    "data/FactoryZero2019/042.xlsx",
    "data/FactoryZero2019/072.xlsx",
    "data/FactoryZero2019/025.xlsx",
    "data/FactoryZero2019/021.xlsx",
    "data/FactoryZero2019/078.xlsx",
    "data/FactoryZero2019/060.xlsx"
]

scoreboard = []


def pop() -> [int]:
    global lock, houses
    with lock:
        houses_left = len(houses)
        if houses_left > 0:
            return houses.pop(0)
    return None


def fun():
    global other_lock, scoreboard
    while (house := pop()) != None:
        df = pd.read_excel(house, sheet_name="smartMeter", index_col="Timestamp")
        with other_lock:
            scoreboard.append({
                "house": house,
                "score": df['power'].mean()
            })


threads = []

for i in range(8):
    threads.append(threading.Thread(
        target=fun,
        args=()
    ))
    threads[i].start()

df = pd.read_excel("data/FactoryZero2019/054.xlsx", sheet_name="smartMeter", index_col="Timestamp")
mean54 = df["power"].mean()

for thread in threads:
    thread.join()

scoreboard.sort(key=lambda it: abs(it["score"] - mean54))

for item in scoreboard:
    print(f"{item['house']},{item['score']}")
