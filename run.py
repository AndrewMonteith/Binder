from flask import Flask, render_template, jsonify
import pandas as pd

from recommender import recommend_n, gen_new_user, add_user_rating

book_details = pd.read_csv("recommender/Dataset/books.csv").set_index('book_id')

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/register")
def register_user():
    new_id = gen_new_user()

    return jsonify({"new_id": new_id})


@app.route("/recommend/<int:user>")
def get_recommendations(user):
    recommendations = recommend_n(user, 3)

    result = []
    for book_id in recommendations.index:
        d = book_details.loc[book_id].to_dict()
        d['id'] = book_id
        result.append(d)

    return jsonify(result)

@app.route("/addrating/<int:user>/<int:book>/<int:rating>")
def add_rating(user, book, rating):
    add_user_rating(user, book, rating) 


@app.route("/newuser/<user>")
def new_user(user):
    return "hello new user " + user


if __name__ == "__main__":
    app.run(debug=True)
