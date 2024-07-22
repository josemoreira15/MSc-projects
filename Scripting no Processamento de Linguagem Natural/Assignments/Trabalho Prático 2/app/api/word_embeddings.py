import json, os
import numpy as np
from gensim.utils import simple_preprocess
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity


class WB_Model():

    def __init__(self, data_path): 
        self.metadata = json.load(open(data_path))
        self.sentences = self.preprocess()
        self.model = None
        self.doc_vectors = None

    def preprocess(self):
        all_notes = [item['notes'] for item in self.metadata]
        return [simple_preprocess(note) for note in all_notes]
    
    def train_model(self):
        os.makedirs('models', exist_ok=True)
        self.model = Word2Vec(self.sentences, epochs=20, vector_size=300)
        self.model.save("models/dr.model")

    def load_model(self, model_path):
        self.model = Word2Vec.load(model_path)
        self.doc_vectors = self.create_vectors(self.sentences)
        
    def vectorize(self, doc):
        doc = [word for word in doc if word in self.model.wv.key_to_index]
        if len(doc) == 0:
            return np.zeros(self.model.vector_size)
        return np.mean(self.model.wv[doc], axis=0)

    def create_vectors(self, sentences):
        return [self.vectorize(text) for text in sentences]
    
    def get_most_similar(self, query, top_n):
        query_vector = self.vectorize(simple_preprocess(query)).reshape(1, -1)
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]
        indices_most_similar = np.argsort(similarities)[-top_n:][::-1]
        return [(self.metadata[i]['id'], self.metadata[i]['notes'], similarities[i]) for i in indices_most_similar]
    


#wb = WB_Model(data_path='data/dre.json')
#wb.train_model()