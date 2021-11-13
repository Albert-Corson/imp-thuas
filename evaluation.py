import numpy as np
import pandas as pd

from plot import plot_error_distribution


def pretty_print(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty_print(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))


def mean_squared_error(ref: pd.DataFrame, pred: pd.DataFrame) -> float:
    return np.square(np.subtract(ref, pred)).mean().values[0]


def raw_bias(errors: [float]) -> float:
    return np.mean(errors)


def abs_raw_bias(abs_errors: [float]) -> float:
    return np.mean(abs_errors)


def percent_bias(ref_values: [float], pred_values: [float]) -> float:
    ref_mean = np.mean(ref_values)
    pred_mean = np.mean(pred_values)
    return 100 * abs((pred_mean - ref_mean) / ref_mean)


def sum_error(abs_errors: [float]) -> float:
    return np.sum(abs_errors)


def max_error(errors: [float]) -> float:
    res = 0
    for val in errors:
        res = val if abs(val) > res else res
    return res


def error_variance(errors: [float]) -> float:
    mean_error = raw_bias(errors)
    squared_diffs = [(errors[i] - mean_error) ** 2 for i in range(len(errors))]
    return (1 / len(errors)) * np.sum(squared_diffs)


def evaluate(df: [pd.DataFrame], imputed_dfs: [[pd.DataFrame]], gaps_config: [[float]], gaps_indices: [[int]], show_plots: bool = False):
    for i in range(len(imputed_dfs)):
        # tweak this
        flattened_indices = [it for sublist in gaps_indices[i] for it in sublist]
        ref_values = [df.iloc[:, 0][index] for index in flattened_indices]
        pred_values = [imputed_dfs[i].iloc[:, 0][index]
                       for index in flattened_indices]

        errors = [ref_values[i] - pred_values[i]
                  for i in range(len(ref_values))]
        abs_errors = [abs(it) for it in errors]

        title = f"Error distribution with gap type {i + 1} [{gaps_config[i][0]};{gaps_config[i][1]}]"
        results = {
            "Mean Squared Error (lower is better)": mean_squared_error(df, imputed_dfs[i]),
            "Raw Bias": raw_bias(errors),
            "Absolute Raw Bias (lower is better)": abs_raw_bias(abs_errors),
            "Percent Bias (bellow 5% is acceptable)": percent_bias(ref_values, pred_values),
            "Sum (lower is better)": sum_error(abs_errors),
            "Maximum (lower is better)": max_error(errors),
            "Variance (lower is better)": error_variance(errors)
        }

        print(title)
        pretty_print(results, indent=1)
        print("")

        if show_plots:
            plot_error_distribution(errors, title)
