
from sklearn.base import BaseEstimator, TransformerMixin



class TypeTransformer(BaseEstimator, TransformerMixin):
    def transform(self, X):
        X = X.astype(int)
        return X

