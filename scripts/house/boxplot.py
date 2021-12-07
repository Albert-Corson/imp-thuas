#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd

def create_boxplot(unimputed_data: pd.DataFrame,imputed_data: pd.DataFrame, columns_to_visualize = []):
    """"Creates boxplots that compare unimputed data vs imputed data, helps visualize things like distribution.
    It generates a boxplot with two plots (unimputed/raw and imputed) so we can compare the two.
    Please specify the columns_to_visualize parameter if only certain amount of columns need to be visualized!
    NOTE!: THIS METHOD IS NOT OPTIMIZED AT ALL AND MIGHT JUST TAKE A BIT TO LOAD"""
    if len(columns_to_visualize) == 0:
        for column in imputed_data.columns.values.tolist():
            unimputed_data[column + "_imp"] = imputed_data[column]
            unimputed_data.boxplot(column=[column,column+"_imp"])
            plt.show()
    else:
        for column in columns_to_visualize:
            unimputed_data[column + "_imp"] = imputed_data[column]
            unimputed_data.boxplot(column=[column,column+"_imp"])
            plt.show()

