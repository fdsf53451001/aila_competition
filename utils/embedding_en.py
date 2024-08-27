# from transformers import AutoTokenizer
# import torch
# from transformers import AutoModel

# model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
# tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")

# def get_embedding(text:str) -> list:
#     inputs = tokenizer([text], return_tensors="pt")
#     with torch.no_grad():
#         outputs = model(**inputs)
#         embeddings = outputs[0][:, 0]
#     return embeddings[0]

from openai import OpenAI
from numpy import dot
from numpy.linalg import norm

client = OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

if __name__ == "__main__":
    a = get_embedding("1. This Regulation lays down rules relating to the protection of natural persons with regard to the processing of personal data and rules relating to the free movement of personal data. ")
    b = get_embedding("本規則適用於全部或一部以自動化方式處理之個人資料，且適用於其他非自動化方式處理而構成檔案系統之一部分或旨在構成檔案系統之一部分的個人資料。")
    cos_sim = dot(a, b)/(norm(a)*norm(b))
    print(cos_sim)