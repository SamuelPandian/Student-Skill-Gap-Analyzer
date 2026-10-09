import numpy as np
from typing import List, Optional

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two numpy vectors: (A . B) / (||A|| ||B||)"""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

class SemanticMatcher:
    def __init__(self):
        self.model = None
        self._load_model_attempted = False

    def _init_transformer_model(self):
        if self._load_model_attempted:
            return
        self._load_model_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            # Fast, lightweight model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.model = None

    def calculate_semantic_score(self, student_text: str, job_text: str) -> float:
        """
        Calculates semantic similarity percentage score (0-100) between
        student resume/skill summary and job description text.
        """
        if not student_text or not job_text:
            return 50.0 # Default baseline if text insufficient

        self._init_transformer_model()

        if self.model is not None:
            try:
                embeddings = self.model.encode([student_text, job_text])
                sim = compute_cosine_similarity(embeddings[0], embeddings[1])
                # Scale similarity to 0-100 range
                score = max(0.0, min(100.0, sim * 100.0))
                return round(score, 2)
            except Exception:
                pass

        # Fallback to TF-IDF cosine similarity if transformer is unavailable
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer().fit_transform([student_text, job_text])
            vectors = vectorizer.toarray()
            sim = compute_cosine_similarity(vectors[0], vectors[1])
            return round(max(0.0, min(100.0, sim * 100.0)), 2)
        except Exception:
            return 65.0
