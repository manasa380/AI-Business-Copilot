import pandas as pd


def calculate_kpis(df):

    numeric_cols = df.select_dtypes(include="number").columns

    kpis = {}

    kpis["Rows"] = len(df)
    kpis["Columns"] = len(df.columns)

    if len(numeric_cols) > 0:
        main_col = numeric_cols[0]

        kpis["Total"] = round(df[main_col].sum(), 2)
        kpis["Average"] = round(df[main_col].mean(), 2)
        kpis["Maximum"] = round(df[main_col].max(), 2)
        kpis["Minimum"] = round(df[main_col].min(), 2)

    return kpis