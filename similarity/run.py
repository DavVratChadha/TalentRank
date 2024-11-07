import pandas as pd
import pickle
import numpy as np
import similarity_functions as sim

DATA_DIR = "data/"

def random_partition(target, n):
    np.random.seed(42)
    np.random.shuffle(target)
    return target[:n], target[n:]

#load target.csv for target as a list
target = pd.read_csv(DATA_DIR + "target.csv")
target = target["target"].tolist()

#load vectors.pkl for vector as a dictionary
with open(DATA_DIR + "vectors.pkl", "rb") as f:
    vectors = pickle.load(f)

#partition target randomly into 8 and 3
train, test = random_partition(target, 8)

#mean and std of target vectors dict while target holds candidate ids
target_vectors = [vectors[int(candidate)] for candidate in train]
# print(f"{target_vectors=}")
mean = np.mean(target_vectors, axis=0)
std = np.std(target_vectors, axis=0)


#now the idea is to find the most similar candidate to the mean vector
#or more like top-k similar candidates to the mean vector
#for this we will calculate the cosine similarity between mean vector and all candidate vectors, and sort them in descending order
#and return the top-k candidates
#cosine similaity can be calculated with cosine_similarity(v1, v2) function in similarity/cosine.py

similarity = []
for candidate in vectors:
    vector = vectors[candidate]
    # similarity.append((candidate, sim.cosine_similarity(mean, vector))) #[(767, 69), (1209, 118), (1453, 134)], s=321
    similarity.append((candidate, sim.euclidean_similarity(mean, vector))) #[(767, 68), (1209, 118), (1453, 134)], s=320
    # similarity.append((candidate, sim.manhattan_similarity(mean, vector))) #[(767, 68), (1209, 118), (1453, 134)], s=320
    # similarity.append((candidate, sim.inner_product_similarity(mean, vector))) #[(767, 257), (1209, 299), (1453, 315)], s=871
    # similarity.append((candidate, sim.minkowski_similarity(mean, vector))) #[(767, 68), (1209, 118), (1453, 134)], s=320

similarity = sorted(similarity, key=lambda x: x[1], reverse=True)


#need to find how low are test candidates in the sorted list of similarity
#and return their index
indices = []
s = 0
for i, (c, d) in enumerate(similarity):
    if c in test:
        indices.append((c,i))
        s += i
        
print(f"{indices=}, {s=}")
# print(mean)