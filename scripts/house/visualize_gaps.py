#!/usr/bin/env python3
import missingno as msno
import pandas as pd
import matplotlib.pyplot as plt


def visualize_by_matrix(df : pd.DataFrame):
    """"Visualize nullity by using missing no matrix. The matrix gives a quick display to whether the data contain nulls or NaN."""
    msno.matrix(df,figsize=(20,10.5),fontsize=12)
    plt.show()

def visualize_by_barchart(df : pd.DataFrame):
    """"Visualize the amount of gaps per column by a barchart from missingno library."""
    msno.bar(df,figsize=(20,10.5),fontsize=12)
    plt.show()

def visualize_by_heatmap(df : pd.DataFrame):
    """This figure can give insight into correlations of column values that create gaps by using missingno library"""
    msno.heatmap(df,figsize=(20,10.5),fontsize=12)
    plt.show()