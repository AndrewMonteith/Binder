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

    tendencies = []

    for user_id in user_mean_dataframe.index.unique():
        book_ratings = r.loc[user_id].set_index("book_id")
        joined = book_ratings.join(book_mean_dataframe["value"])

        tendency = (joined["rating"] - joined["value"]).sum() / len(book_ratings.index)

        tendencies.append([user_id, len(joined.index), tendency])

    df = pd.DataFrame.from_records(tendencies)
    df.columns = ["user_id", "n", "value"]
    df.set_index("user_id").to_csv("Dataset/user_tendencies.csv")


def precompute_book_tendencies():
    r = ratings.set_index("book_id")
    r.sort_index()

    tendencies = []
    for book_id in book_mean_dataframe.index.unique():
        user_ratings = r.loc[book_id].set_index("user_id")
        joined = user_ratings.join(user_mean_dataframe["value"])

        tendency = (joined["rating"] - joined["value"]).sum() / len(user_ratings.index)

        tendencies.append([book_id, len(joined.index), tendency])

    df = pd.DataFrame.from_records(tendencies)
    df.columns = ["book_id", "n", "value"]
    df.set_index("book_id").to_csv("Dataset/book_tendencies.csv")


precompute_user_tendencies()
precompute_book_tendencies()
