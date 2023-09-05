# Multi-agent Movie Recommendation System

## Overview

This project is a movie recommendation system, This is a movie recommendation system developed using Python, Flask, and pandas.
The application takes a movie title input from the user and provides a list of recommended movies that are similar to the input 
movie. This system also allows users to maintain a personal watchlist where they can add or remove movies. The recommendation system 
is built based on genres. It creates a genre graph where each node represents a genre. It uses a Breadth-First Search (BFS) algorithm 
on this graph to find genres similar to the genre of the input movie and recommends movies from these similar genres.

## Dataset
The movie dataset used in this project is from [Kaggle](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows) 
by HARSHIT SHANKHDHAR. It is under the CC0: Public Domain License.

## Getting Started

### Prerequisites

The system depends on several Python libraries, namely:

- Python 3.7+
- Flask: used to create the web interface of the application and handle HTTP requests and responses.
- pandas: primarily used to read and clean up the data from a CSV file and convert it into a list of movie objects.

### Installation

Install the necessary Python packages:

```
pip install pandas flask numpy
```

### Usage

Run the main python script to start the Flask web app:

```
python main.py
```

This will start the Flask server. Navigate to the URL provided in your console (typically http://127.0.0.1:5000/ or http://localhost:5000/) to start interacting with the recommendation system.

## How It Works

The system is built around several classes:

- `Movie`: Represents a movie with all relevant details.
- `Analyser`: Analyses user input to find a movie that matches the entered title.
- `GenreNode` and `GenreGraph`: Creates a graph where each genre is a node, and each edge indicates a connection between genres. This is used for genre-based movie recommendations.
- `Goal` and `RecommendationPlan`: Define a goal for the recommender system and generates movie recommendations based on the user's last viewed movie and genre graph.
- `Recommender`: A movie recommender agent which makes movie recommendations and updates the user's watchlist.
- `User` and `WatchlistManagement`: Represent a user and manage the watchlists of all users.

The system performs the following steps:

1. Processes a CSV file containing movie data and creates a list of Movie objects.
2. Creates a genre map and adds similar movies to each Movie object.
3. Creates a genre graph for all the movies.
4. Interacts with the user through a Flask web app, allowing them to enter a movie title.
5. Gives recommendations of similar movies to the user.

## Web Application Routes

- `/`: Sets up the application by creating a user with a username provided by the user.
- `/home`: The home page of the application where a user can get movie recommendations.
- `/watchlist`: Displays a user's watchlist.
- `/add_to_watchlist`: Adds a movie to a user's watchlist.
- `/remove_from_watchlist`: Removes a movie from a user's watchlist.

## Key Files

- `main.py`: The main script for running the movie recommendation system.
- `assets/movies.csv`: The CSV file containing movie data.

## Contributors
    217010763 - Benedict Sizwe Kubeka
