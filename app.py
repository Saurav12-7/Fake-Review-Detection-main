from flask import Flask, render_template, request, jsonify
from scraper import scrape_reviews  # Function to scrape reviews from a given URL
from model import load_models, classify_reviews  # Functions to load models and classify reviews
from preprocessing import preprocess_text  # Function for text preprocessing
import pandas as pd
import os
import nltk # Keep the import if other parts of your code use nltk directly

# --- NLTK Data Downloads (REMOVED from here) ---
# These lines are removed from app.py.
# Ensure NLTK data is downloaded by your deployment environment (e.g., Dockerfile, build script).
# --- End NLTK Data Downloads ---


# Get the absolute path to the directory where app.py is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app, explicitly defining static folder and URL path
# This tells Flask exactly where to find your static files (CSS, JS)
# --- CONFIRMED: 'statics' folder and '/static' URL path ---
app = Flask(
    __name__,
    static_folder=os.path.join(basedir, 'statics'), # Corrected to 'statics'
    static_url_path='/static' # The URL path remains '/static' for consistency
)

# Load the pre-trained Word2Vec and SVM models
# This will only happen once when the application starts
word2vec_model, svm_model = load_models()

@app.route('/')
def index():
    """
    Render the home page (index.html).
    Flask will look for index.html in the 'templates' folder by default.
    """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    API endpoint to analyze reviews from a given product URL.
    - Scrapes reviews using `scrape_reviews()`.
    - Preprocesses reviews using `preprocess_text()` (from preprocessing.py).
    - Classifies reviews using the trained SVM model (from model.py).
    - Returns the analysis results as JSON.
    """
    data = request.json
    url = data.get('url')  # Extract the URL from the request

    if not url:
        return jsonify({"error": "No URL provided"}), 400  # Return error if URL is missing

    reviews = scrape_reviews(url)  # Scrape reviews from the given URL
    if reviews.empty:
        return jsonify({"error": "No reviews found"}), 404  # Return error if no reviews found

    # Validate expected columns from scraped reviews
    if "Review Text" not in reviews.columns or "Rating" not in reviews.columns:
        return jsonify({"error": "Invalid reviews format"}), 400  # Return error if data format is incorrect

    # Preprocessing reviews before classification
    preprocessed_reviews = []
    for i, review_text_raw in enumerate(reviews["Review Text"]):
        # Pass the original review text to preprocess_text
        review_text_processed = preprocess_text(review_text_raw)  # Clean and preprocess review text

        # Ensure rating is a float for consistency, default if conversion fails
        try:
            rating = float(reviews.iloc[i]["Rating"])
        except ValueError:
            rating = 3.0 # Default rating if conversion fails

        preprocessed_reviews.append({"Review Text": review_text_processed, "Rating": rating, "Original Review Text": review_text_raw})

    # Predict whether reviews are real or fake
    # The classify_reviews function expects a list of dictionaries with 'Review Text' and 'Rating'
    # It will internally handle the vectorization based on the preprocessed text and the rating/length features
    predictions = classify_reviews(preprocessed_reviews, word2vec_model, svm_model)

    # Create a DataFrame to store results
    # Use the original review text for display in the UI
    df = pd.DataFrame({
        "Review": [r["Original Review Text"] for r in preprocessed_reviews], # Use original review text for display
        "Rating": [r["Rating"] for r in preprocessed_reviews],
        "Prediction": predictions
    })

    # Map predictions to human-readable labels
    df["Prediction"] = df["Prediction"].map({1: "Fake (Computer Generated)", 0: "Real (Original)"})

    # Convert DataFrame to dictionary format for JSON response
    result = df.to_dict(orient='records')
    return jsonify(result)

if __name__ == '__main__':
    """
    Run the Flask application on the assigned port.
    Uses an environment variable for port if available (for deployment),
    otherwise defaults to port 5000.
    """
    port = int(os.environ.get("PORT", 5000))  # Get the assigned port for deployment
    app.run(host='0.0.0.0', port=port, debug=True)  # Run the Flask app
