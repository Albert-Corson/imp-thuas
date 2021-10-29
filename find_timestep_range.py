from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_excel("data/FactoryZero2019/054.xlsx",
                   sheet_name="alklimaHeatPump", index_col="Timestamp")

best_start = df.index[0]
best_end = df.index[0]
best_start_idx = df.index[0]
best_end_idx = df.index[0]

cur_start = df.index[0]
cur_start_idx = df.index[0]

for idx in range(1, len(df.index)):
    prev = df.index[idx - 1]
    cur = df.index[idx]
    diff = cur - prev

    if 250 < diff and diff < 420:
        if prev - cur_start > best_end - best_start:
            best_start = cur_start
            best_end = prev
            best_start_idx = cur_start_idx
            best_end_idx = idx - 1
    else:
        cur_start_idx = idx
        cur_start = cur

print(f"start_timestamp = {best_start}")
print(f"end_timestamp = {best_end}")
print(f"start_idx = {best_start_idx}")
print(f"end_idx = {best_end_idx}")

to_plot = df.index[best_start_idx:best_end_idx]
dates = []
timesteps = []
for i in range(1, len(to_plot)):
    dates.append(datetime.fromtimestamp(to_plot[i]))
    timesteps.append(to_plot[i] - to_plot[i - 1])
plt.scatter(dates, timesteps, marker='.', s=2, alpha=0.8)
plt.show()
