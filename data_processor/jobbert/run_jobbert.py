import torch
from transformers import AutoModel, AutoTokenizer

# Load the JobBERT model and tokenizer for skill extraction
model_id = "jjzha/jobbert_skill_extraction"
model = AutoModel.from_pretrained(model_id)  # Use AutoModel instead of AutoModelForTokenClassification
tokenizer = AutoTokenizer.from_pretrained(model_id)

input_text = "Looking for a data scientist skilled in Python, machine learning, data analysis, and SQL."
inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)

# Run the model to get embeddings
with torch.no_grad():
    outputs = model(**inputs)
    # Extract the last hidden state (embeddings)
    embeddings = outputs.last_hidden_state

# Convert embeddings to NumPy array
embeddings_np = embeddings.cpu().numpy()
print(f"Embeddings shape: {embeddings_np.shape}")
