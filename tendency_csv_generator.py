"""
    The recommendation algorithm I use relies on a large grid of tendency values.
    To produce recommendations it is useful to have these values precomputed for a large dataset
    This file precomputes the tendencies and stores then in CSV files.
    This operation can take roughly a couple of minutes to compute.

"""

import pandas as pd
from pandas_helpers import create_meand_df

ratings = pd.read_csv("Dataset/ratings.csv")

book_mean_dataframe = create_meand_df(ratings, "book_id")
user_mean_dataframe = create_meand_df(ratings, "user_id")


def precompute_user_tendencies():
    r = ratings.set_index("user_id")
    r.sort_index()

    tendencies = {}
    for user_id in user_mean_dataframe.index.unique():
        book_ratings = r.loc[user_id].set_index("book_id")
        joined = book_ratings.join(book_mean_dataframe["value"])

        tendency = (joined["rating"] - joined["value"]).sum() / len(book_ratings.index)

        tendencies[user_id] = tendency

    df = pd.DatFrame(list(tendencies.items()), columns=["user_id", "tendency"]).set_index("user_id")
    df.to_csv("user_tendencies.csv")


def precompute_book_tendencies():
    r = ratings.set_index("book_id")
    r.sort_index()

    tendencies = {}
    for book_id in book_mean_dataframe.index.unique():
        user_ratings = r.loc[book_id].set_index("user_id")
        joined = user_ratings.join(user_mean_dataframe["value"])

        tendency = (joined["rating"] - joined["value"]).sum() / len(user_ratings.index)

        tendencies[book_id] = tendency

    df = pd.DataFrame(list(tendencies.items()), columns=["book_id", "tendency"]).set_index("book_id")
    df.to_csv("book_tendencies.csv")


precompute_user_tendencies()
precompute_book_tendencies()
