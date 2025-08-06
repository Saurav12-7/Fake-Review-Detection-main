import re
import emoji
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize

# Initialize lemmatizer and stemmer
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

# Function to convert emojis into text representation
def handle_emojis(text):
    """Converts emojis into text descriptions."""
    return emoji.demojize(text)

# Function to correct spelling mistakes
def correct_spelling(r):
    """Performs spelling correction on the input text."""
    return str(TextBlob(r).correct())

# Function to apply lemmatization, stemming, and remove stopwords
def lemmatize_and_stem(r):
    """Performs tokenization, removes stopwords, applies lemmatization, and stemming."""
    words = word_tokenize(r)
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    stemmed_words = [stemmer.stem(word) for word in words]
    r = ' '.join(lemmatized_words)  # Using lemmatized words
    r = ' '.join(stemmed_words)   # Using stemmed words
    return r

# Function to preprocess text
def preprocess_text(r):
    """Performs text preprocessing including lowercasing, removing special characters,
    handling numbers, expanding contractions, correcting spelling, handling emojis,
    and applying lemmatization and stemming."""
    
    # Convert text to lowercase and remove unnecessary spaces
    r = str(r).lower().strip()
    
    # Replace common symbols with text representations
    r = r.replace('%', ' percent')
    r = r.replace('$', ' dollar ')
    r = r.replace('₹', ' rupee ')
    r = r.replace('€', ' euro ')
    r = r.replace('@', ' at ')
    r = r.replace(',000,000,000 ', 'b ')  # Convert billions
    r = r.replace(',000,000 ', 'm ')  # Convert millions
    r = r.replace(',000 ', 'k ')  # Convert thousands
    
    # Handling numerical abbreviations
    r = re.sub(r'([0-9]+)000000000', r'\1b', r)
    r = re.sub(r'([0-9]+)000000', r'\1m', r)
    r = re.sub(r'([0-9]+)000', r'\1k', r)
    
    # Dictionary for expanding contractions (e.g., "can't" -> "cannot")
    contractions = {
        "ain't": "am not", "aren't": "are not", "can't": "can not", "can't've": "can not have", "cause": "because",
        "could've": "could have", "couldn't": "could not", "couldn't've": "could not have", "didn't": "did not",
        "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hasn't": "has not", "haven't": "have not",
        "he's": "he is", "how's": "how is", "i'm": "i am", "i've": "i have", "isn't": "is not", "it's": "it is",
        "let's": "let us", "should've": "should have", "shouldn't": "should not", "that's": "that is",
        "there's": "there is", "they're": "they are", "they've": "they have", "wasn't": "was not",
        "we're": "we are", "we've": "we have", "weren't": "were not", "what's": "what is", "where's": "where is",
        "who's": "who is", "why's": "why is", "won't": "will not", "would've": "would have", "wouldn't": "would not",
        "you're": "you are", "you've": "you have"
    }
    
    # Expand contractions in text
    r_decontracted = [contractions.get(word, word) for word in r.split()]
    r = ' '.join(r_decontracted)
    
    # Remove HTML tags
    r = re.sub(r'<.*?>', '', r)
    
    # Correct spelling mistakes
    r = correct_spelling(r)
    
    # Convert emojis into text representations
    r = handle_emojis(r)
    
    # Apply lemmatization and stemming after removing stopwords
    r = lemmatize_and_stem(r)
    
    return r