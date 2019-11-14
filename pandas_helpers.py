import pandas as pd

def create_meand_df(ratings, key_id):
    means = ratings[[key_id, "rating"]].groupby(key_id).mean()
    means.columns = ["value"]

    counts = ratings[key_id].value_counts().to_frame()
    counts.columns = ["n"]

    return means.join(counts)


def update_meand_df(df, index, value):
    row = df.loc[index]

    new_n = row["n"] + 1
    new_mean = (row["n"] * row["value"] + value) / new_n

    df.at[index, "n"] = new_n
    df.at[index, "value"] = new_mean


def count_rows(dataframe):
    return len(dataframe.index)
