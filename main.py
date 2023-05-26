import pandas as pd
from collections import defaultdict

from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)


class Movie:
    """A class to represent a movie with its attributes like title, director, genre, etc."""

    def __init__(self, title, director, release_year, genre, rating, plot, poster_link, similar_movies=None):
        if similar_movies is None:
            similar_movies = []
        self.title = title
        self.director = director
        self.release_year = release_year
        self.genre = genre
        self.rating = rating
        self.plot = plot
        self.poster_link = poster_link
        self.similar_movies = similar_movies


class Analyser:
    """A class for the analyser agent used for analysing the user input and checking if it matches the title of any
    movie in the database."""

    def __init__(self, userInput, movies):
        self.userInput = userInput
        self.movies = movies

    def getUserInput(self):
        return self.userInput

    def analyse(self):
        return next((movie for movie in self.movies if movie.title.lower() == self.userInput.lower()), None)


def create_genre_map(movies):
    """
    creates a mapping of genres to movies, useful for movie recommendation based on genre.
    """
    genre_map = defaultdict(list)
    for movie in movies:
        for genre in movie.genre:
            genre_map[genre].append(movie)
    return genre_map


def process_movie_data(file_path):
    """
    reads a csv file, cleans up data, and processes the data into a list of movie objects.
    """
    try:
        movie_data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error occurred while reading file {file_path}:\n{e}")
        return []

    try:
        # clean up data
        movie_data.drop(
            ['Certificate', 'Runtime', 'Meta_score', 'Star1', 'Star2', 'Star3', 'Star4', 'No_of_Votes', 'Gross'],
            axis=1, inplace=True)
        movie_data['Genre'] = movie_data['Genre'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

        movie_data.dropna(subset=['Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating', 'Overview', 'Director'],
                          inplace=True)

        # create Movie objects
        movie_objects = []
        for index, row in movie_data.iterrows():
            try:
                release_year = int(row['Released_Year'])
            except ValueError:
                print(f"Invalid year value {row['Released_Year']} for movie {row['Series_Title']}")
                continue  # skip this movie and move to the next one

            try:
                rating = float(row['IMDB_Rating'])
            except ValueError:
                print(f"Invalid rating value {row['IMDB_Rating']} for movie {row['Series_Title']}")
                continue  # skip this movie and move to the next one

            movie_objects.append(
                Movie(row['Series_Title'], row['Director'], release_year, row['Genre'], rating, row['Overview'],
                      row['Poster_Link']))
    except Exception as e:
        print(f"Error occurred while processing movie data:\n{e}")
        return []

    # create genre map and add similar movies to each Movie object
    genre_map = create_genre_map(movie_objects)
    for movie in movie_objects:
        similar_movies = set()
        for genre in movie.genre:
            for similar_movie in genre_map[genre]:
                if similar_movie.title != movie.title:
                    similar_movies.add(similar_movie)
        movie.similar_movies = list(similar_movies)

    return movie_objects


class GenreNode:
    """
    defines a node in a genre graph. Each node represents a genre and has connections to other genres.
    """

    def __init__(self, genre):
        self.genre = genre
        self.connected_genres = defaultdict(int)

    def add_connection(self, other_genre):
        self.connected_genres[other_genre] += 1


class GenreGraph:
    """
    creates a graph where each genre is a node and each edge indicates a connection between genres.
    """

    def __init__(self, movies):
        self.genre_nodes = self.build_graph(movies)

    def build_graph(self, movies):
        genre_nodes = {}
        movie_genre_map = create_genre_map(movies)

        for genre in movie_genre_map.keys():
            if genre not in genre_nodes:
                genre_nodes[genre] = GenreNode(genre)
            for movie in movie_genre_map[genre]:
                for other_genre in movie.genre:
                    if other_genre != genre:
                        genre_nodes[genre].add_connection(other_genre)

        return genre_nodes

    def bfs(self, start_genre):

        if start_genre not in self.genre_nodes:
            print(f"The genre {start_genre} does not exist in the genre graph.")
            return []  # Return an empty list

        visited = set()
        queue = [self.genre_nodes[start_genre]]
        similar_genres = []

        while queue:
            current_genre_node = queue.pop(0)
            visited.add(current_genre_node.genre)

            for connected_genre in current_genre_node.connected_genres.keys():
                if connected_genre not in visited:
                    queue.append(self.genre_nodes[connected_genre])
                    similar_genres.append(connected_genre)

        return similar_genres


class Goal:
    """
    defines a goal for the recommender system. Each goal has a name, desired state, current state, and action.
    """

    def __init__(self, name, desired_state, state, action):
        self.name = name
        self.state = state
        self.action = action
        self.desired_state = desired_state

    def getName(self):
        return self.name

    def getState(self):
        return self.state.getActive()

    def action(self):
        return self.action

    def getDesiredState(self):
        return self.desired_state

    def isAchieved(self, recommender):  # Check if the desired state for the goal is achieved.
        if self.name == "recommend":
            return recommender.hasRecommendations()
        else:

            return False


class RecommendationPlan:
    """
    generates movie recommendations based on a user's last viewed movie and a genre graph.
    """

    def __init__(self, last_viewed_movie, genreGraph):
        self.last_viewed_movie = last_viewed_movie
        self.genreGraph = genreGraph
        self.movieRecommendations = self.generate_recommendations()

    def generate_recommendations(self):
        similar_genres = self.genreGraph.bfs(self.last_viewed_movie.genre[0])
        similar_movies = set()
        for genre in similar_genres:
            for movie in self.last_viewed_movie.similar_movies:
                if genre in movie.genre and movie != self.last_viewed_movie:
                    similar_movies.add(movie)
        return list(similar_movies)

    def getRecommendations(self):
        return self.movieRecommendations


class Recommender:
    """
    a movie recommender agent which makes movie recommendations and updates a user's watchlist.
    """

    def __init__(self, movieDataset, genreGraph, watchlistManagement):
        self.movieRecomendations = []
        self.movieDataset = movieDataset
        self.genreGraph = genreGraph
        self.watchlistManagement = watchlistManagement
        self.goal = None
        self.recommendationGoals = []

    def hasRecommendations(self):
        return bool(self.movieRecomendations)

    def getMovieRecommendations(self):
        # retrieves similar movies to the input movie
        return self.movieRecomendations

    def setMovieRecommendation(self, plan):
        recommendations = plan.getRecommendations()
        for movie in recommendations:
            if movie not in self.movieRecomendations:
                self.movieRecomendations.append(movie)

    def addGoal(self, goal):
        self.recommendationGoals.append(goal)

    def removeGoal(self, goal):
        self.recommendationGoals.remove(goal)

    def setActiveGoal(self, goal):
        self.goal = goal

    def getGoal(self):
        return self.goal

    def act(self, user, plan=None, movie=None):
        if self.goal.action == "recommend":  # For "recommend" action
            if plan:
                self.setMovieRecommendation(plan)
        elif self.goal.action == "update":  # For "update" action
            if movie:
                if self.goal.desired_state == "add":
                    self.watchlistManagement.addToWatchlist(user, movie)
                elif self.goal.desired_state == "remove":
                    self.watchlistManagement.removeFromWatchlist(user, movie)
            self.watchlistManagement.storeUserWatchlist(user)


class User:
    """
    defines a user with a username.
    """

    def __init__(self, username):
        self.username = username

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username


class WatchlistManagement:
    """
    manages the watchlists of all users.
    """

    def __init__(self):
        self.userWatchlists = {}

    def getUserWatchlist(self, user):
        return self.userWatchlists.get(user.getUsername(), [])

    def addToWatchlist(self, user, movie):
        if user.getUsername() not in self.userWatchlists:
            self.userWatchlists[user.getUsername()] = []
        self.userWatchlists[user.getUsername()].append(movie)

    def removeFromWatchlist(self, user, movie):
        if user.getUsername() in self.userWatchlists and movie in self.userWatchlists[user.getUsername()]:
            self.userWatchlists[user.getUsername()].remove(movie)

    def storeUserWatchlist(self, user):
        if user.getUsername() in self.userWatchlists:
            watchlist = self.userWatchlists[user.getUsername()]
            df = pd.DataFrame([movie.__dict__ for movie in watchlist])
            df.to_csv(f'{user.getUsername()}_watchlist.csv', index=False)

    def updateUserWatchlist(self, user):
        try:
            df = pd.read_csv(f'{user.getUsername()}_watchlist.csv')
            movies = []
            for _, row in df.iterrows():
                movie = Movie(row['title'], row['director'], row['release_year'], row['genre'], row['rating'],
                              row['plot'], row['poster_link'], row['similar_movies'])
                movies.append(movie)
            self.userWatchlists[user.getUsername()] = movies
        except FileNotFoundError:
            print(f"No existing watchlist for user: {user.getUsername()}")


@app.route('/', methods=['GET', 'POST'])
def setup():
    """
    sets up the application by creating a user with a username provided by a user.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        global user
        user = User(username)
        watchlistManagement.updateUserWatchlist(user)
        return redirect(url_for('home'))

    return render_template('setUp.html')


template_path = 'home.html'


@app.route('/home', methods=['GET', 'POST'])
def home():
    """
    the home page of the application where a user can get movie recommendations.
    """
    if request.method == 'POST':
        movie_title = request.form.get('movie_title')
        if movie_title:
            recommendations = get_recommendations(movie_title)
            return render_template('home.html', recommendations=recommendations)

    return render_template('home.html', recommendations=[])


def get_recommendations(title):
    """
    returns a list of movie recommendations for a given movie title.
    """
    analyser = Analyser(title, movies)
    result_movie = analyser.analyse()
    recommender = Recommender(movies, genreGraph, watchlistManagement)
    plan = RecommendationPlan(result_movie, genreGraph)
    goal_recommend = Goal("recommend", "has recommendations", "active", "recommend")
    recommender.addGoal(goal_recommend)
    recommender.setActiveGoal(goal_recommend)
    recommender.act(user, plan)
    print("Has recommendations?", goal_recommend.isAchieved(recommender))
    recommended_movies = recommender.getMovieRecommendations()
    return recommended_movies


@app.route('/watchlist', methods=['GET'])
def watchlist():
    """
    displays a user's watchlist.
    """
    watchlist = watchlistManagement.getUserWatchlist(user)
    return render_template('watchlist.html', watchlist=watchlist)


@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    """
    adds a movie to a user's watchlist.
    """
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        movie = next((movie for movie in movies if movie.title.lower() == movie_title.lower()), None)
        if movie:
            goal_update_add = Goal("update", "add", "active", "update")
            recommender.addGoal(goal_update_add)
            recommender.setActiveGoal(goal_update_add)
            recommender.act(user, None, movie)
        return redirect(url_for('home'))


@app.route('/remove_from_watchlist', methods=['POST'])
def remove_from_watchlist():
    """
    removes a movie from a user's watchlist.
    """
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        movie = next((movie for movie in movies if movie.title.lower() == movie_title.lower()), None)
        if movie:
            goal_update_remove = Goal("update", "remove", "active", "update")
            recommender.addGoal(goal_update_remove)
            recommender.setActiveGoal(goal_update_remove)
            recommender.act(user, None, movie)
        return redirect(url_for('watchlist'))


if __name__ == "__main__":
    file_path = './assets/movies.csv'
    movies = process_movie_data(file_path)
    genreGraph = GenreGraph(movies)
    watchlistManagement = WatchlistManagement()
    user = User('JohnDoe')
    recommender = Recommender(movies, genreGraph, watchlistManagement)
    goal_recommend = Goal("recommend", "has recommendations", "active", "recommend")
    recommender.addGoal(goal_recommend)
    recommender.setActiveGoal(goal_recommend)
    app.run(debug=True)
