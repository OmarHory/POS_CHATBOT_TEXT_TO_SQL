# import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import Levenshtein

# import os
# dirname = os.path.dirname(os.path.dirname(__file__))
# filename = os.path.join(dirname, "data")
# os.environ['NLTK_DATA'] = filename

# nltk.download('punkt')
# nltk.download('stopwords')


def is_close_lev_distance(word, keywords, threshold=0.7):
    for keyword in keywords:
        # Calculate the Lev ratio between the word and each greeting phrase
        similarity = Levenshtein.ratio(word.lower(), keyword.lower())
        # Check if the similarity is greater than threshold
        if similarity >= threshold:
            return True

    return False


def is_specific_message(message, keywords):
    # Tokenize the message
    words = word_tokenize(message.lower())

    # Remove stopwords
    words = [word for word in words if word not in stopwords.words("english")]
    for word in words:
        if is_close_lev_distance(word, keywords):
            return True

    return False
