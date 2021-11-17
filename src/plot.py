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


def plot_hotdeck_comparison(donor, donor_before, donor_after, before, after, og_before, og_after):
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.grid(True)

    plt.plot(donor, color="b", label="Full donor")

    plt.plot(og_before, "g", label="Best match")
    plt.plot(og_after, "g")

    plt.plot(donor_before, "--c", label="Donor sample")
    plt.plot(donor_after, "--c")

    plt.plot(before, ":r", label="Comparison sample")
    plt.plot(after, ":r")

    plt.legend(loc=1)
    plt.show()
