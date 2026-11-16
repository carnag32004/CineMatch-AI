
import pandas as pd
import numpy as np

# Load the saved movie dataset
movies = pd.read_pickle("movies.pkl")

# Load the saved similarity matrix
similarity = np.load("similarity.npy")


def get_recommendations(movie_title, top_n=5):

    # Find the selected movie
    matches = movies.index[
        movies["title"].str.lower() == movie_title.lower()
    ].tolist()

    if not matches:
        return "Movie not found!"

    movie_index = matches[0]

    # Get similarity scores
    scores = list(enumerate(similarity[movie_index]))

    # Sort movies by similarity
    scores = sorted(
        scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Remove the selected movie
    scores = [
        item for item in scores
        if item[0] != movie_index
    ]

    # Get top recommendations
    movie_indices = [item[0] for item in scores[:top_n]]

    return movies.iloc[movie_indices][
        ["title", "director", "actors"]
    ].reset_index(drop=True)
