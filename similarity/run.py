import pandas as pd
import pickle
import numpy as np
from  similarity_functions import cosine_similarity

DATA_DIR = "data/"


#load target.csv for target as a list
target = pd.read_csv(DATA_DIR + "target.csv")
target = target["target"].tolist()

#load vectors.pkl for vector as a dictionary
with open(DATA_DIR + "vectors.pkl", "rb") as f:
    vectors = pickle.load(f)

#mean and std of target vectors dict while target holds candidate ids
target_vectors = [vectors[int(candidate)] for candidate in target[:8]]
# print(f"{target_vectors=}")
mean = np.mean(target_vectors, axis=0)
std = np.std(target_vectors, axis=0)


#now the idea is to find the most similar candidate to the mean vector
#or more like top-k similar candidates to the mean vector
#for this we will calculate the cosine similarity between mean vector and all candidate vectors, and sort them in descending order
#and return the top-k candidates
#cosine similaity can be calculated with cosine_similarity(v1, v2) function in similarity/cosine.py

distances = []
for candidate in vectors:
    vector = vectors[candidate]
    distances.append((candidate, cosine_similarity(mean, vector)))

distances = sorted(distances, key=lambda x: x[1], reverse=True)


#need to find how low are target[8:] candidates in the sorted list of distances
#and return their index
indices = []
for i, (c, d) in enumerate(distances):
    if c in target[8:]:
        indices.append((c,i))

print(f"{indices=}")