import pandas as pd

from recommender.pandas_helpers import create_meand_df

ratings = pd.read_csv("Dataset/ratings.csv")

book_mean_dataframe = create_meand_df(ratings, "book_id")
user_mean_dataframe = create_meand_df(ratings, "user_id")

book_tendencies = pd.read_csv("Dataset/book_tendencies.csv").set_index("book_id")
user_tendencies = pd.read_csv("Dataset/user_tendencies.csv").set_index("user_id")


def compute_predicted_values(user_id):
    user_mean = user_mean_dataframe.at[user_id, "value"]
    user_tendency = user_tendencies.at[user_id, "tendency"]

    predicted_values = {}

    # b chooses how much user means influence our predictions
    b = 0.4
    is_ut_pos = user_tendency > 0

    for book_id in book_tendencies.index.unique():
        book_mean = book_mean_dataframe.at[book_id, "value"]
        book_tendency = book_tendencies.at[book_id, "tendency"]

        is_bt_pos = book_tendency > 0

        def store(value):
            predicted_values[book_id] = value

        if is_ut_pos and is_bt_pos:
            store(max(user_mean + book_tendency, book_mean + user_tendency))
        elif not (is_ut_pos or is_bt_pos):
            store(min(user_mean + book_tendency, book_mean + user_tendency))
        elif (not is_ut_pos) and is_bt_pos and user_mean < book_mean:
            x = (book_mean + user_tendency) * b + (user_mean + book_tendency) * (1-b)
            store(min(max(user_mean, x), book_mean))
        elif (user_mean > book_mean) and (not is_ut_pos) and is_ut_pos:
            store(b * book_mean + (1-b) * user_mean)

    return pd.DataFrame(list(predicted_values.items()), columns=["book_id", "predicted"]).set_index("book_id")

def recommend_n(user_id, n):
    predicted_vals = compute_predicted_values(user_id)

    return predicted_vals.nlargest(n, 'predicted')

