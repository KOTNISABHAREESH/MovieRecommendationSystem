from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
import gc  # Garbage collector for memory management

app = Flask(__name__)

# Load and preprocess data - optimize memory usage
movies = pd.read_csv('movies.csv', dtype={'movieId': 'int32', 'title': 'str', 'genres': 'str'})
movies['title'] = movies['title'].fillna('')
movies['genres'] = movies['genres'].fillna('')

# Create a combined feature for TF-IDF
movies['combined_features'] = movies['title'] + ' ' + movies['genres']

# TF-IDF Vectorization for text-based features - use sparse matrices
tfidf = TfidfVectorizer(stop_words='english', max_features=5000)  # Limit features to reduce memory
tfidf_matrix = tfidf.fit_transform(movies['combined_features'])
# Calculate similarity on-demand instead of storing the full matrix
# cosine_sim will be calculated when needed in the recommendation function

# Create genre-based features using one-hot encoding
# Split the genres string into a list of genres
movies['genre_list'] = movies['genres'].apply(lambda x: x.split('|') if x else [])

# Use MultiLabelBinarizer to create one-hot encoded features
mlb = MultiLabelBinarizer()
genre_features = mlb.fit_transform(movies['genre_list'])

# Initialize K-Nearest Neighbors model for genre-based recommendations
knn_model = NearestNeighbors(n_neighbors=10, algorithm='auto', metric='jaccard')
knn_model.fit(genre_features)

# Force garbage collection to free memory
gc.collect()

# Function to get movie recommendations using cosine similarity (TF-IDF based)
def get_tfidf_recommendations(title, num_recommendations=5):
    try:
        # Find the index of the movie that matches the title
        indices = pd.Series(movies.index, index=movies['title'])
        
        # Check if the movie title exists in our dataset
        if title not in indices:
            # Try to find by exact title first
            exact_match = movies[movies['title'].str.lower() == title.lower()]
            if len(exact_match) > 0:
                title = exact_match.iloc[0]['title']
            else:
                # Find closest match if exact title not found
                closest_titles = movies[movies['title'].str.contains(title, case=False)]
                if len(closest_titles) > 0:
                    title = closest_titles.iloc[0]['title']
                else:
                    # Try matching just the movie name without year
                    title_without_year = title.split('(')[0].strip()
                    closest_titles = movies[movies['title'].str.contains(title_without_year, case=False)]
                    if len(closest_titles) > 0:
                        title = closest_titles.iloc[0]['title']
                    else:
                        return []
        
        idx = indices[title]
        
        # Get the TF-IDF vector for the selected movie
        movie_vector = tfidf_matrix[idx:idx+1]
        
        # Calculate similarity on-demand for just this movie (more memory efficient)
        sim_scores = cosine_similarity(movie_vector, tfidf_matrix).flatten()
        
        # Create a list of (index, similarity score) tuples
        sim_scores = list(enumerate(sim_scores))
        
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get the scores of the 10 most similar movies (excluding the movie itself)
        sim_scores = sim_scores[1:11]
        
        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]
        
        # Return the top movies
        return movies.iloc[movie_indices].head(num_recommendations)
    except Exception as e:
        print(f"Error in TF-IDF recommendations: {str(e)}")
        return []

# Function to get movie recommendations using KNN (genre-based)
def get_knn_recommendations(title, num_recommendations=5):
    try:
        # Find the index of the movie that matches the title
        indices = pd.Series(movies.index, index=movies['title'])
        
        # Check if the movie title exists in our dataset
        if title not in indices:
            # Try to find by exact title first
            exact_match = movies[movies['title'].str.lower() == title.lower()]
            if len(exact_match) > 0:
                title = exact_match.iloc[0]['title']
            else:
                # Find closest match if exact title not found
                closest_titles = movies[movies['title'].str.contains(title, case=False)]
                if len(closest_titles) > 0:
                    title = closest_titles.iloc[0]['title']
                else:
                    # Try matching just the movie name without year
                    title_without_year = title.split('(')[0].strip()
                    closest_titles = movies[movies['title'].str.contains(title_without_year, case=False)]
                    if len(closest_titles) > 0:
                        title = closest_titles.iloc[0]['title']
                    else:
                        return []
        
        idx = indices[title]
        
        # Get the genre features of the input movie
        movie_genre_features = genre_features[idx].reshape(1, -1)
        
        # Find K nearest neighbors
        distances, indices = knn_model.kneighbors(movie_genre_features)
        
        # Exclude the input movie itself
        similar_movies_indices = [i for i in indices.flatten() if i != idx][:num_recommendations]
        
        # Return the top movies
        return movies.iloc[similar_movies_indices]
    except Exception as e:
        print(f"Error in KNN recommendations: {str(e)}")
        return []

# Function to get hybrid recommendations (combining TF-IDF and KNN)
def get_hybrid_recommendations(title, num_recommendations=5):
    try:
        # Get recommendations from both methods
        tfidf_recs = get_tfidf_recommendations(title, num_recommendations=num_recommendations)
        
        # Force garbage collection between heavy operations
        gc.collect()
        
        knn_recs = get_knn_recommendations(title, num_recommendations=num_recommendations)
        
        # If both methods fail, return an empty DataFrame with the correct columns
        if len(tfidf_recs) == 0 and len(knn_recs) == 0:
            return pd.DataFrame(columns=movies.columns.tolist() + ['reason'])
        
        # If either method fails, return results from the other
        if len(tfidf_recs) == 0:
            knn_recs['reason'] = "Similar genres"
            return knn_recs
        if len(knn_recs) == 0:
            tfidf_recs['reason'] = "Similar content"
            return tfidf_recs
        
        # Combine and deduplicate recommendations
        combined_recs = pd.concat([tfidf_recs, knn_recs]).drop_duplicates().head(num_recommendations)
        
        # Add a recommendation reason
        combined_recs['reason'] = combined_recs.apply(
            lambda x: "Similar content and genres" if x.name in tfidf_recs.index and x.name in knn_recs.index 
            else "Similar content" if x.name in tfidf_recs.index 
            else "Similar genres", axis=1
        )
        
        return combined_recs
    except Exception as e:
        print(f"Error in hybrid recommendations: {str(e)}")
        # If there's an error, try to return at least some recommendations
        if 'tfidf_recs' in locals() and len(tfidf_recs) > 0:
            tfidf_recs['reason'] = "Similar content"
            return tfidf_recs
        elif 'knn_recs' in locals() and len(knn_recs) > 0:
            knn_recs['reason'] = "Similar genres"
            return knn_recs
        else:
            return pd.DataFrame(columns=movies.columns.tolist() + ['reason'])

# Function to get movies by genre
def get_movies_by_genre(genre, limit=10):
    try:
        # Normalize the genre (remove extra spaces, lowercase)
        normalized_genre = genre.strip().lower()
        
        # Try exact match first (case insensitive)
        all_genres = []
        for genres in movies['genre_list']:
            all_genres.extend([g.lower() for g in genres])
        
        unique_genres = set(all_genres)
        
        # Find the closest matching genre if not an exact match
        closest_genre = None
        for g in unique_genres:
            if g == normalized_genre:
                closest_genre = g
                break
            elif normalized_genre in g or g in normalized_genre:
                closest_genre = g
        
        # If we found a closest match, use it
        if closest_genre:
            # Filter movies that contain this genre (case insensitive)
            genre_movies = movies[movies['genres'].str.lower().str.contains(closest_genre, case=False)]
        else:
            # Otherwise use the original genre string
            genre_movies = movies[movies['genres'].str.lower().str.contains(normalized_genre, case=False)]
        
        # If still no matches, try to be more lenient
        if len(genre_movies) == 0:
            # Try matching any part of the genre string
            for word in normalized_genre.split():
                if len(word) > 3:  # Only use words with more than 3 characters
                    genre_movies = movies[movies['genres'].str.lower().str.contains(word, case=False)]
                    if len(genre_movies) > 0:
                        break
        
        # Return the top movies in that genre
        return genre_movies.head(limit)
    except Exception as e:
        print(f"Error in get_movies_by_genre: {str(e)}")
        return pd.DataFrame()

# Function to get popular genres
def get_popular_genres(limit=8):  # Increased limit for more options
    try:
        # Extract all genres
        all_genres = []
        for genres in movies['genre_list']:
            all_genres.extend(genres)
        
        # Count genre occurrences
        genre_counts = pd.Series(all_genres).value_counts()
        
        # Filter out very generic or ambiguous genres
        filtered_genres = genre_counts[~genre_counts.index.isin(['Hindi Dubbed'])]
        
        # Return the most popular genres
        return filtered_genres.head(limit).index.tolist()
    except Exception as e:
        print(f"Error in get_popular_genres: {str(e)}")
        # Return some default genres if there's an error
        return ['Action', 'Comedy', 'Drama', 'Romance', 'Thriller']

# Function to get a random selection of movies
def get_random_selection(limit=5):
    return movies.sample(min(limit, len(movies)))

# Function to get featured movies with specific image paths
def get_featured_movies():
    # Select specific popular movies for the featured section
    featured_movie_ids = [1, 3, 99, 159, 161, 182, 183, 211]  # Baahubali, RRR, Dangal, Brahmastra, Pathaan, Kantara, Sita Ramam, Soorarai Pottru
    
    # Filter the movies dataframe to get only the featured movies
    featured_movies = movies[movies['movieId'].isin(featured_movie_ids)]
    
    # Create a dictionary to map movie IDs to image paths
    movie_image_map = {
        1: "baahubali.png",    # Baahubali: The Beginning
        3: "rrr.png",          # RRR
        99: "dangal.png",      # Dangal
        159: "brahmastra.png", # Brahmastra
        161: "pathaan.png",    # Pathaan
        182: "kantara.png",    # Kantara
        183: "sitaramam.png",  # Sita Ramam
        211: "soorari.png"     # Soorarai Pottru
    }
    
    # Add image path to each movie
    featured_movies_with_images = []
    for idx, movie in featured_movies.iterrows():
        movie_dict = movie.to_dict()
        movie_dict['image_path'] = movie_image_map.get(movie['movieId'], "netflix.jpg")
        featured_movies_with_images.append(movie_dict)
    
    return featured_movies_with_images

@app.route('/')
def home():
    # Get popular genres for the homepage
    popular_genres = get_popular_genres()
    
    # Get specific featured movies with image paths
    featured_movies = get_featured_movies()
    
    return render_template('index.html', 
                          popular_genres=popular_genres,
                          featured_movies=featured_movies)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    title = request.form['title']
    if not title:
        return render_template('index.html', error="Please enter a movie title")
    
    try:
        # Get hybrid recommendations
        recommendations = get_hybrid_recommendations(title)
        
        if len(recommendations) == 0:
            # Get popular genres for the homepage
            popular_genres = get_popular_genres()
            
            # Get specific featured movies with image paths
            featured_movies = get_featured_movies()
            
            return render_template('index.html', 
                                  error=f"No recommendations found for '{title}'",
                                  popular_genres=popular_genres,
                                  featured_movies=featured_movies)
        
        # Convert recommendations to a list of dictionaries for the template
        recommendations_list = []
        for idx, movie in recommendations.iterrows():
            # Create a dictionary to map movie IDs to image paths
            movie_image_map = {
                1: "baahubali.png",    # Baahubali: The Beginning
                3: "rrr.png",          # RRR
                99: "dangal.png",      # Dangal
                159: "brahmastra.png", # Brahmastra
                161: "pathaan.png",    # Pathaan
                182: "kantara.png",    # Kantara
                183: "sitaramam.png",  # Sita Ramam
                211: "soorari.png"     # Soorarai Pottru
            }
            
            recommendations_list.append({
                'title': movie['title'],
                'genres': movie['genres'],
                'reason': movie.get('reason', 'Similar movie'),
                'image_path': movie_image_map.get(movie['movieId'], "netflix.jpg") if 'movieId' in movie else "netflix.jpg"
            })
        
        # Get popular genres for the homepage
        popular_genres = get_popular_genres()
        
        # Get specific featured movies with image paths
        featured_movies = get_featured_movies()
        
        return render_template('index.html', 
                              recommendations=recommendations_list, 
                              input_movie=title,
                              popular_genres=popular_genres,
                              featured_movies=featured_movies)
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error in recommendation: {str(e)}")
        
        # Get popular genres for the homepage
        popular_genres = get_popular_genres()
        
        # Get specific featured movies with image paths
        featured_movies = get_featured_movies()
        
        return render_template('index.html', 
                              error=f"An error occurred while finding recommendations for '{title}'",
                              popular_genres=popular_genres,
                              featured_movies=featured_movies)

@app.route('/genre', methods=['POST'])
def genre():
    try:
        genre = request.form.get('genre', '').strip()
        if not genre:
            # Get popular genres for the homepage
            popular_genres = get_popular_genres()
            
            # Get specific featured movies with image paths
            featured_movies = get_featured_movies()
            
            return render_template('index.html', 
                                  error="Please enter a genre",
                                  popular_genres=popular_genres,
                                  featured_movies=featured_movies)
        
        # Get movies by genre
        genre_movies = get_movies_by_genre(genre)
        
        if len(genre_movies) == 0:
            # Try to suggest similar genres
            all_genres = []
            for genres in movies['genre_list']:
                all_genres.extend(genres)
            
            unique_genres = set(all_genres)
            suggested_genres = []
            
            for g in unique_genres:
                if any(word in g.lower() for word in genre.lower().split() if len(word) > 3):
                    suggested_genres.append(g)
            
            # Get popular genres for the homepage
            popular_genres = get_popular_genres()
            
            # Get specific featured movies with image paths
            featured_movies = get_featured_movies()
            
            error_message = f"No movies found for genre '{genre}'"
            if suggested_genres:
                error_message += ". Did you mean: " + ", ".join(suggested_genres[:3]) + "?"
            
            return render_template('index.html', 
                                  error=error_message,
                                  popular_genres=popular_genres,
                                  featured_movies=featured_movies)
        
        # Convert genre_movies to a list of dictionaries for the template
        genre_movies_list = []
        for idx, movie in genre_movies.iterrows():
            # Create a dictionary to map movie IDs to image paths
            movie_image_map = {
                1: "baahubali.png",    # Baahubali: The Beginning
                3: "rrr.png",          # RRR
                99: "dangal.png",      # Dangal
                159: "brahmastra.png", # Brahmastra
                161: "pathaan.png",    # Pathaan
                182: "kantara.png",    # Kantara
                183: "sitaramam.png",  # Sita Ramam
                211: "soorari.png"     # Soorarai Pottru
            }
            
            genre_movies_list.append({
                'title': movie['title'],
                'genres': movie['genres'],
                'image_path': movie_image_map.get(movie['movieId'], "netflix.jpg") if 'movieId' in movie else "netflix.jpg"
            })
        
        # Get popular genres for the homepage
        popular_genres = get_popular_genres()
        
        # Get specific featured movies with image paths
        featured_movies = get_featured_movies()
        
        return render_template('index.html', 
                              genre_movies=genre_movies_list, 
                              input_genre=genre,
                              popular_genres=popular_genres,
                              featured_movies=featured_movies)
    except Exception as e:
        print(f"Error in genre route: {str(e)}")
        
        # Get popular genres for the homepage
        popular_genres = get_popular_genres()
        
        # Get specific featured movies with image paths
        featured_movies = get_featured_movies()
        
        return render_template('index.html', 
                              error=f"An error occurred while finding movies for genre '{genre}'",
                              popular_genres=popular_genres,
                              featured_movies=featured_movies)

if __name__ == '__main__':
    app.run(debug=True)