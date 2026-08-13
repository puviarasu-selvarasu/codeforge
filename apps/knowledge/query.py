from .ingestion import _vectorizer, _vectors, _chunks
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def query_knowledge(query, top_k=5):
    if not _chunks or _vectorizer is None or _vectors is None:
        return []
    query_vec = _vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, _vectors).flatten()
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    results = []
    for idx in top_indices:
        if similarities[idx] > 0:
            results.append(_chunks[idx]['text'])
    return results