from string import punctuation
from nltk.corpus import stopwords

import pandas as pd
import pickle
import nltk

from sklearn.feature_extraction.text import TfidfVectorizer
from unidecode import unidecode

nltk.download('stopwords')


class Model:
    tokenizer = TfidfVectorizer().build_tokenizer()

    stop_words = [unidecode(stopW) for stopW in stopwords.words('english')]
    non_words = list(punctuation)
    non_words.extend(['¿', '¡', '...', '..'])
    stop_words = stop_words + non_words

    def __init__(self, type):
        self.type = type
        self.base_path = 'resources/'
        self.model = self.load_model(type)

    def load_model(self, model_type: str):
        try:
            if not isinstance(model_type, str):
                raise ValueError('Type must be a string')

            root = self.base_path

            if model_type == 'author':
                path = root + 'models/tf-idf/model-v10.0.pkl'
            elif model_type == 'article':
                path = root + 'models/tf-idf/model-v10.0.pkl'
            else:
                path = root + "models/model-v11.0.pkl"

            with open(path, "rb") as fp:
                return pickle.load(fp)

        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error while loading model: {str(e)}")

    def get_model(self):
        return self.model

    def preprocess_topic(self, topic):
        return [word.lower() for word in self.tokenizer(unidecode(topic)) if word.lower() not in self.stop_words]

    def get_most_relevant_docs_by_topic(self, topic, author_size):
        preprocessed_topic = self.preprocess_topic(topic)

        if all(token in self.model['vocabulary'] for token in preprocessed_topic):
            token_ids = [self.model['vocabulary'][token] for token in preprocessed_topic]
            data = {}
            for token_id in token_ids:
                data[token_id] = [item[0] for item in self.model['matrix'].getcol(token_id).sorted_indices().toarray()]
            df_result = pd.DataFrame(data=data, index=self.model['indexes'])
            if author_size:
                return df_result[(df_result != 0).all(1)].sum(axis=1).sort_values(ascending=False).head(author_size)
            else:
                return df_result[(df_result != 0).all(1)].sum(axis=1).sort_values(ascending=False)
        else:
            return pd.Series()

    def get_most_relevant_docs_by_topic_v2(self, topic, authorSize):
        preprocessed_topic = self.preprocess_topic(topic)

        if all(token in self.model['vocabulary'] for token in preprocessed_topic):
            token_ids = [self.model['vocabulary'][token]
                         for token in preprocessed_topic]
            data = {}
            for tokenId in token_ids:
                data[tokenId] = [item[0] for item in self.model['matrix'].getcol(
                    tokenId).sorted_indices().toarray()]
            df_result = pd.DataFrame(data=data, index=self.model['indexes'])
            if authorSize:
                return df_result[(df_result != 0).all(1)].sum(axis=1).sort_values(ascending=False).head(authorSize)
            else:
                return df_result[(df_result != 0).all(1)].sum(axis=1).sort_values(ascending=False)
        else:
            return pd.Series()
