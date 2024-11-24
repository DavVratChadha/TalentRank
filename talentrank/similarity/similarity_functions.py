import numpy as np

#function to calculate cosine similarity between two vectors
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

#function to calculate euclidean similarity between two vectors
def euclidean_similarity(v1, v2):
    return 1/(np.linalg.norm(v1 - v2) + 1)

#function to calculate manhattan similarity between two vectors
def manhattan_similarity(v1, v2):
    return 1/(np.sum(np.abs(v1 - v2)) + 1)

#function to calculate inner product similarity between two vectors
def inner_product_similarity(v1, v2):
    return np.dot(v1, v2)

#function to calculate minkowski similarity between two vectors
def minkowski_similarity(v1, v2, p=2):
    # Calculate the Minkowski distance
    minkowski_distance = np.sum(np.abs(v1 - v2) ** p) ** (1 / p)
    
    # Convert distance to similarity (lower distance -> higher similarity)
    # Avoid division by zero by adding a small epsilon
    return 1 / (1 + minkowski_distance)