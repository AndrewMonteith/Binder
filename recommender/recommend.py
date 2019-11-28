import pandas as pd

from recommender.pandas_helpers import create_meand_df, update_meand_df, remove_meand_df_entry
from recommender.tendency import compute_user_tendency, compute_book_tendency

ratings = pd.read_csv("recommender/Dataset/ratings.csv")

book_mean_dataframe = create_meand_df(ratings, "book_id")
user_mean_dataframe = create_meand_df(ratings, "user_id")

book_tendencies = pd.read_csv("recommender/Dataset/book_tendencies.csv").set_index("book_id")
user_tendencies = pd.read_csv("recommender/Dataset/user_tendencies.csv").set_index("user_id")


def clamp(minv, maxv, val):
    if val <= minv:
        return minv
    elif maxv <= val:
        return maxv
    else:
        return val


def compute_predicted_values(user_id):
    user_mean = user_mean_dataframe.at[user_id, "value"]
    user_tendency = user_tendencies.at[user_id, "value"]

    predicted_values = {}

    user_ratings = ratings.loc[ratings['user_id'] == user_id]

    rated_books = set({})
    for index, row in user_ratings.iterrows():
        rated_books.add(row['book_id'])

    # b chooses how much user means influence our predictions
    b = 0.8
    is_ut_pos = user_tendency > 0

    for book_id in book_tendencies.index.unique():
        if book_id in rated_books:
            continue

        book_mean = book_mean_dataframe.at[book_id, "value"]
        book_tendency = book_tendencies.at[book_id, "value"]

        is_bt_pos = book_tendency > 0

        def store(value):
            predicted_values[book_id] = clamp(0, 5, value)

        # both rate above the mean
        if is_ut_pos and is_bt_pos:
            store(max(user_mean + book_tendency, book_mean + user_tendency))

        # both rate below the mean
        elif not (is_ut_pos or is_bt_pos): # both rate below the mean
            store(min(user_mean + book_tendency, book_mean + user_tendency))

        # can interpolate between the 2 means
        elif ((not is_ut_pos) and is_bt_pos and user_mean < book_mean) or ((not is_bt_pos) and is_ut_pos and book_mean < user_mean):
            x = (book_mean + user_tendency) * b + (user_mean + book_tendency) * (1 - b)
            store(clamp(min(book_mean, user_mean), max(book_mean, user_mean), x))

        # tendencies don't compare well
        elif (book_mean < user_mean and (not is_ut_pos) and is_bt_pos) or ((user_mean < book_mean) and is_ut_pos and (not is_bt_pos)):
            store(b * book_mean + (1 - b) * user_mean)

        # small edge case
        elif book_mean == user_mean:
            store(book_mean)

    return pd.DataFrame(list(predicted_values.items()), columns=["book_id", "predicted"]).set_index("book_id")


def recommend_n(user_id, n):
    predicted_vals = compute_predicted_values(user_id)

    largest_10 = predicted_vals.nlargest(10, 'predicted')

    return largest_10.sample(frac=1).head(n)

print(recommend_n(100, 3))

def gen_new_user():
    new_id = len(user_tendencies) + 1

    user_tendencies.loc[new_id] = 0
    user_mean_dataframe.loc[new_id] = 0

    return new_id


def add_user_rating(user_id, book_id, rating):
    global ratings

    # append row to dataframe, turns out there's no really easy way to do this
    new_row = pd.DataFrame.from_records([[user_id, book_id, rating]], columns=["user_id", "book_id", "rating"])
    new_ratings = pd.concat([ratings, new_row]).reset_index(drop=True)

    ratings = new_ratings

    new_book_mean = update_meand_df(book_mean_dataframe, book_id, rating)
    new_user_mean = update_meand_df(user_mean_dataframe, user_id, rating)

    update_meand_df(user_tendencies, user_id, rating - new_book_mean)
    update_meand_df(book_tendencies, book_id, rating - new_user_mean)


def remove_user_rating(user_id, book_id, rating):
    global ratings

    rating_index = ratings[(ratings['user_id'] == user_id) & (ratings['book_id'] == book_id)].index
    ratings = ratings.drop(rating_index)

    remove_meand_df_entry(user_mean_dataframe, user_id, rating)
    remove_meand_df_entry(book_mean_dataframe, book_id, rating)

    # recompute tendencies
    user_tendencies.at[user_id, "n"] -= 1
    user_tendencies.at[user_id, "value"] = compute_user_tendency(ratings, book_mean_dataframe, user_id)

    book_tendencies.at[book_id, "n"] -= 1
    book_tendencies.at[book_id, "value"] = compute_book_tendency(ratings, user_mean_dataframe, book_id)


def change_user_rating(user_id, book_id, rating):
    # need to use old rating to remove it
    old_rating = ratings[(ratings["user_id"] == user_id) & (ratings["book_id"] == book_id)]["rating"]
    remove_user_rating(user_id, book_id, old_rating)
    add_user_rating(user_id, book_id, rating)


def get_rated_books(user_id):
    return ratings[ratings['user_id'] == user_id]
