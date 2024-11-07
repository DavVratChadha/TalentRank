import pandas as pd
import pickle
import numpy as np
import similarity_functions as sim

DATA_DIR = "data/"

def random_partition(target, n):
    np.random.seed(42)
    np.random.shuffle(target)
    return target[:n], target[n:]

def questionaire_ranking():
    #load target.csv for target as a list
    target = pd.read_csv(DATA_DIR + "target.csv")
    target = target["target"].tolist()

    #remove 705
    # target.remove(705) #something feels wrong with this candidate, so removing it as its not like others

    #load vectors.pkl for vector as a dictionary
    with open(DATA_DIR + "vectors.pkl", "rb") as f:
        vectors = pickle.load(f)

    #partition target randomly into 8 and 3
    train, test = random_partition(target, 8)

    #mean and std of target vectors dict while target holds candidate ids
    target_vectors = [vectors[int(candidate)] for candidate in train]
    mean = np.mean(target_vectors, axis=0)


    #now the idea is to find the most similar candidate to the mean vector
    #or more like top-k similar candidates to the mean vector
    #for this we will calculate the cosine similarity between mean vector and all candidate vectors, and sort them in descending order
    #and return the top-k candidates
    similarity = []
    for candidate in vectors:
        vector = vectors[candidate]
        similarity.append((candidate, sim.euclidean_similarity(mean, vector)))

    similarity = sorted(similarity, key=lambda x: x[1], reverse=True)

    return similarity

if __name__ == "__main__":
    questionaire_ranking()