import json
from collections import defaultdict
from sentence_transformers import SentenceTransformer


model_id = "jjzha/jobbert_skill_extraction"

#use sentence transformer to get the embeddings
model = SentenceTransformer(model_id)

#read candidates.json
data_dir = "data/"
with open(f"{data_dir}candidates.json", "r") as f:
    candidates = json.load(f)
    
#encode the education and work history of each candidate
candidate_embeddings = defaultdict(dict)
for candidate_id in candidates:
    candidate = candidates[candidate_id]
    candidate_embeddings[candidate_id]["education"] = model.encode(candidate["education"]).tolist()
    candidate_embeddings[candidate_id]["work_history"] = model.encode(candidate["work_history"]).tolist()

#write to a new json
with open(f"{data_dir}candidate_embeddings.json", "w") as f:
    json.dump(candidate_embeddings, f)