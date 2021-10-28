import matplotlib.pyplot as plt
import pandas as pd


def plot_imputation(df, gapped: pd.DataFrame, imputed: pd.DataFrame, y_label: str, title="Untitled"):
    plt.figure(title)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(y_label)
    plt.plot(df, c="green", label="Reference data")
    plt.plot(imputed, c="red", label="Imputed data")
    plt.plot(gapped, c="cyan", label="Data with gaps")
    plt.legend()


def plot_error_distribution(errors: [float], title: str):
    plt.figure(title)
    plt.title(title)
    plt.hist(errors, 50, density=True, alpha=0.75)


def show_all_plots():
    plt.show()
