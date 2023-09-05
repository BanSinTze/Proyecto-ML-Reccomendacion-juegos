import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

games_model = pd.read_parquet(r'games_model.parquet.gzip')
games_model=games_model.explode('genres')
games_model.dropna(inplace=True)
co = CountVectorizer(max_features=7000, stop_words='english')

vector = co.fit_transform(games_model['genres']).toarray()
co.get_feature_names_out()
cosine_sim = cosine_similarity(vector)