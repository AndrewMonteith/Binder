import pandas as pd

def compute_user_tendency(ratings, book_means_df, user_id):
    r = ratings.set_index("user_id")

    book_ratings = r.loc[user_id]
    if isinstance(book_ratings, pd.Series):
        return book_ratings.at["rating"] - book_means_df.at[book_ratings["book_id"], "value"]

    book_ratings = book_ratings.set_index("book_id")
    joined = book_ratings.join(book_means_df["value"])

    return (joined["rating"] - joined["value"]).sum() / len(book_ratings.index)


def compute_book_tendency(ratings, user_means_df, book_id):
    r = ratings.set_index("book_id")

    user_ratings = r.loc[book_id].set_index("user_id")
    joined = user_ratings.join(user_means_df["value"])

    return (joined["rating"] - joined["value"]).sum() / len(user_ratings.index)
