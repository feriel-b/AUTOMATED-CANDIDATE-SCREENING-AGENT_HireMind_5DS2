# In app/semantic_matcher.py
print("--- LOADING SEMANTIC MATCHER AI MODULE ---")

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# This will download the model (approx. 90MB) the first time it's run.
# It's a very powerful and efficient model.
print("Loading sentence-transformer model 'all-MiniLM-L6-v2'...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.")

def get_text_embedding(text: str) -> np.ndarray:
    """Converts a block of text into a semantic vector."""
    if not text:
        return None
    # The model.encode function does all the heavy lifting
    embedding = model.encode(text)
    return embedding.tolist() # Convert numpy array to a plain list for DB storage

def calculate_semantic_score(vector1: List[float], vector2: List[float]) -> int:
    """Calculates the cosine similarity between two vectors."""
    if not vector1 or not vector2:
        return 0
    
    # Reshape arrays for the function
    v1 = np.array(vector1).reshape(1, -1)
    v2 = np.array(vector2).reshape(1, -1)
    
    # Calculate similarity and scale to a 0-100 score
    score = cosine_similarity(v1, v2)[0][0]
    return int(score * 100)