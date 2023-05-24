import pandas as pd
import numpy as np
from collections import defaultdict

class Movie:
    def __init__(self, title, director, release_year, genre, rating, plot, poster_link, similar_movies=[]):
        self.title = title
        self.director = director
        self.release_year = release_year
        self.genre = genre
        self.rating = rating
        self.plot = plot
        self.poster_link = poster_link
        self.similar_movies = similar_movies


    def getTitle(self):
        return self.title

    def getDirector(self):
        return self.director

    def getReleaseYear(self):
        return self.release_year

    def getGenre(self):
        return self.genre

    def getRating(self):
        return self.rating

    def getPlot(self):
        return self.plot

    def getPosterLink(self):
        return self.poster_link

    def getSimilarMovies(self):
        return self.similar_movies

    def setRating(self, newRating):
        self.rating = newRating

class Analyser:
    def __init__(self, userInput, movies):
        self.userInput = userInput
        self.movies = movies

    def getUserInput(self):
        return self.userInput

    def Analyse(self):
        for movie in self.movies:
            if movie.getTitle().lower() == self.userInput.lower():
                return movie
        return None

def create_genre_map(movies):
    genre_map = defaultdict(list)
    for movie in movies:
        for genre in movie.getGenre():
            genre_map[genre].append(movie)
    return genre_map

def process_movie_data(file_path):
    try:
        movie_data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error occurred while reading file {file_path}:\n{e}")
        return []

    try:
        # clean up data
        movie_data.drop(['Certificate', 'Runtime', 'Meta_score', 'Star1', 'Star2', 'Star3', 'Star4', 'No_of_Votes', 'Gross'], axis=1, inplace=True)
        movie_data['Genre'] = movie_data['Genre'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

        movie_data.dropna(subset=['Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating', 'Overview', 'Director'], inplace=True)

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

            movie_objects.append(Movie(row['Series_Title'], row['Director'], release_year, row['Genre'], rating, row['Overview'], row['Poster_Link']))
    except Exception as e:
        print(f"Error occurred while processing movie data:\n{e}")
        return []

    # create genre map and add similar movies to each Movie object
    genre_map = create_genre_map(movie_objects)
    for movie in movie_objects:
        similar_movies = set()
        for genre in movie.getGenre():
            for similar_movie in genre_map[genre]:
                if similar_movie.getTitle() != movie.getTitle():
                    similar_movies.add(similar_movie)
        movie.similar_movies = list(similar_movies)

    return movie_objects

class GenreNode:
    def __init__(self, genre):
        self.genre = genre
        self.connected_genres = defaultdict(int)

    def add_connection(self, other_genre):
        self.connected_genres[other_genre] += 1

class GenreGraph:
    def __init__(self, movies):
        self.genre_nodes = self.build_graph(movies)

    def build_graph(self, movies):
        genre_nodes = {}
        movie_genre_map = create_genre_map(movies)

        for genre in movie_genre_map.keys():
            if genre not in genre_nodes:
                genre_nodes[genre] = GenreNode(genre)
            for movie in movie_genre_map[genre]:
                for other_genre in movie.getGenre():
                    if other_genre != genre:
                        genre_nodes[genre].add_connection(other_genre)

        return genre_nodes

    def bfs(self, start_genre):
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

class StateType:
    def __init__(self):
        self.active = "active"
        self.inactive = "inactive"

    def getActive(self):
        return self.active

    def getInactive(self):
        return self.inactive

    def setActive(self):
        self.active = "active"

    def setInactive(self):
        self.active = "inactive"

class ActionType:
    def __init__(self):
        self.recommend = "recommend"
        self.update = "update"

    def getRecommend(self):
        return self.recommend

    def getUpdate(self):
        return self.update

    def setRecommend(self):
        self.recommend = "recommend"

    def setUpdate(self):
        self.update = "update"

class Goal:
    def __init__(self, name, desired_state, state=StateType(), action=ActionType()):
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

    def isAchieved(self, recommender):
        if self.name == "recommend":
            return recommender.hasRecommendations()
        else:
            # Check if the desired state for the "update" goal is achieved.
            # Placeholder for now as it would depend on what the update action does.
            return False


class RecommendationPlan:
    def __init__(self, last_viewed_movie, genreGraph):
        self.last_viewed_movie = last_viewed_movie
        self.genreGraph = genreGraph
        self.movieRecommendations = self.generate_recommendations()

    def generate_recommendations(self):
        similar_genres = self.genreGraph.bfs(self.last_viewed_movie.getGenre()[0])
        similar_movies = []
        for genre in similar_genres:
            for movie in self.last_viewed_movie.getSimilarMovies():
                if genre in movie.getGenre() and movie != self.last_viewed_movie and movie not in similar_movies:
                    similar_movies.append(movie)
        return similar_movies

    def getRecommendations(self):
        return self.movieRecommendations


class Recommender:
    def __init__(self, movieDataset, genreGraph):
        self.movieRecomendations = []
        self.movieDataset = movieDataset
        self.genreGraph = genreGraph
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

    def act(self, plan=None):
        if self.goal.action.getRecommend() == "recommend":
            if plan:
                self.setMovieRecommendation(plan)
        else:
            pass  # placeholder for update action


class User:
    def __init__(self, username, watchlist=[]):
        self.username = username
        self.watchlist = watchlist

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username

    def getWatchlist(self):
        return self.watchlist

    def setWatchlist(self, newWatchlist):
        self.watchlist = newWatchlist


class WatchlistManagement:
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


# Usage example:
file_path = './assets/movies.csv'
movies = process_movie_data(file_path)
genreGraph = GenreGraph(movies)  # Create GenreGraph once
analyser = Analyser('Inception', movies)
result_movie = analyser.Analyse()

recommender = Recommender(movies, genreGraph)  # Pass the genreGraph to the Recommender
goal_recommend = Goal("recommend", "has recommendations")
recommender.addGoal(goal_recommend)
recommender.setActiveGoal(goal_recommend)
last_viewed_movie = result_movie  # Assume the last viewed movie is the one analysed
plan = RecommendationPlan(last_viewed_movie, genreGraph)
recommender.act(plan)
print("Has recommendations?", goal_recommend.isAchieved(recommender))

# Fetch the recommended movies
recommended_movies = recommender.getMovieRecommendations()

# Print the titles of the recommended movies
for movie in recommended_movies:
    print(movie.getTitle())