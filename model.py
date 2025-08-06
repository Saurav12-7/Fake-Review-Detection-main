import pandas as pd
from gensim.models import Word2Vec
import numpy as np
import joblib
from sklearn.svm import SVC
from preprocessing import preprocess_text

# Function to train and save Word2Vec and SVM models
def train_and_save_models():
    """
    Trains a Word2Vec model and an SVM model using row_data.csv and saves them.
    """
    print("Starting model training...")

    # Load the data from the CSV file
    try:
        df = pd.read_csv('row_data.csv')
        df = df[['text_', 'label']].rename(columns={'text_': 'review', 'label': 'label'})
        df['label'] = df['label'].map({'CG': 1, 'OR': 0})
    except FileNotFoundError:
        print("Error: row_data.csv not found. Please make sure it's in the same directory.")
        return

    # Preprocess text and train Word2Vec model
    sentences = [preprocess_text(review).split() for review in df['review']]
    word2vec_model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
    word2vec_model.save('word2vec_model.model')
    print("Word2Vec model trained and saved.")

    # Create feature vectors including rating and length for the SVM model
    def get_feature_vector(text, model):
        words = text.split()
        vectors = [model.wv[word] for word in words if word in model.wv]
        if vectors:
            return np.mean(vectors, axis=0)
        return np.zeros(model.vector_size)
    
    # Assuming 'review' and 'label' columns exist
    # And assuming a rating and length feature based on your classification function
    # Let's generate dummy data for rating and length for training purposes
    df['rating'] = np.random.randint(1, 6, size=len(df))
    df['length'] = df['review'].apply(lambda x: len(x.split()))

    # Combine features: rating, length, and text vector
    text_vectors = np.array([get_feature_vector(preprocess_text(x), word2vec_model) for x in df['review']])
    combined_features = np.hstack([df[['rating', 'length']].values, text_vectors])

    X = combined_features
    y = df['label']

    # Train and save the SVM model
    svm_model = SVC(kernel='linear')
    svm_model.fit(X, y)
    joblib.dump(svm_model, 'SVM_model.pkl')
    print("SVM model trained and saved as SVM_model.pkl.")

# Function to load trained models
def load_models():
    """
    Loads the pre-trained Word2Vec model and the SVM model.
    """
    word2vec_model = Word2Vec.load('word2vec_model.model')
    svm_model = joblib.load('SVM_model.pkl')
    return word2vec_model, svm_model

# Function to classify reviews using Word2Vec and SVM
def classify_reviews(reviews, word2vec_model, svm_model):
    """
    Classifies reviews based on text features, rating, and length using an SVM model.
    """
    predictions = []
    
    for review in reviews:
        preprocessed_review = preprocess_text(review['Review Text'])
        words = preprocessed_review.split()
        vectors = np.array([word2vec_model.wv[word] for word in words if word in word2vec_model.wv])
        
        if vectors.size > 0:
            text_vector = np.mean(vectors, axis=0).reshape(1, -1)
            
            try:
                rating = float(review['Rating'])
            except ValueError:
                rating = 3.0

            review_length = len(words)
            rating_vector = np.array([[rating]])
            length_vector = np.array([[review_length]])
            
            combined_features = np.hstack([rating_vector, length_vector, text_vector])
            prediction = svm_model.predict(combined_features)
            predictions.append(prediction[0])
        else:
            predictions.append(0)
    return predictions

# Main execution: Only load models when the script is not run directly
if __name__ == "__main__":
    train_and_save_models()