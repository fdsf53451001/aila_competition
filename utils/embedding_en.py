from transformers import AutoTokenizer
import torch
from transformers import AutoModel

model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")

def get_embedding(text:str) -> list:
    inputs = tokenizer([text], return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs[0][:, 0]
    return embeddings[0]

if __name__ == "__main__":
    print(get_embedding("Hello, my dog is cute"))