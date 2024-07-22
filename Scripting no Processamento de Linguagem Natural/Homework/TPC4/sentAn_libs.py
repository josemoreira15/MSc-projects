from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

texto = "I loved it!"

blob = TextBlob(texto)
sentiment = blob.sentiment
print("<<< TextBlob >>>")
print(f"Polarity: {sentiment.polarity}")
print(f"Subjectivity: {sentiment.subjectivity}")


analyzer = SentimentIntensityAnalyzer()
sentiment2 = analyzer.polarity_scores(texto)
print("<<< Vader >>>")
print("Sentimento:", sentiment2)

# TextBlob
# Vader
# NLTK
# SpaCy
# BERT
# Flair
# PyTorch
# Scikit-Learn

# Língua Portuguesa (PT-BR): OpLexicon