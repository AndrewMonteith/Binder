from flask import Flask, render_template, jsonify

from recommender import *

app = Flask(__name__)

book_details = pd.read_csv("recommender/Dataset/books.csv").set_index('book_id')


def get_book_details(book_id):
    d = book_details.loc[book_id].to_dict()
    d['id'] = int(book_id)  # might be np.int64 so need to make sure it's JSON serializable
    return d


@app.route("/")
def default_ep():
    return render_template("index.html")


@app.route("/register")
def register_user_ep():
    new_id = gen_new_user()

    return jsonify({"new_id": new_id})


@app.route("/recommend/<int:user>")
def get_recommendations_ep(user):
    recommendations = recommend_n(user, 3)

    return jsonify([get_book_details(book_id) for book_id in recommendations.index])


@app.route("/addrating/<int:user>/<int:book>/<int:rating>")
def add_rating_ep(user, book, rating):
    add_user_rating(user, book, rating)

    return jsonify({"success": True})


@app.route("/changerating/<int:user>/<int:book>/<int:rating>")
def change_rating_ep(user, book, rating):
    change_user_rating(user, book, rating)

    return jsonify({"success": True})


@app.route("/removerating/<int:user>/<int:book>/<int:rating>")
def remove_rating_ep(user, book, rating):
    remove_user_rating(user, book, rating)

    return jsonify({"success": True})


@app.route("/userexists/<int:user>")
def does_user_exist_ep(user):
    return jsonify({"exists": does_user_exist(user)})


@app.route("/loadratedbooks/<int:user>")
def load_rated_books_ep(user):
    rated_books = get_rated_books(user)

    response = []
    for _, row in rated_books.iterrows():
        details = get_book_details(row['book_id'])
        details['rating'] = float(row['rating'])

        response.append(details)

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
