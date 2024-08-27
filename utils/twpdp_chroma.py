import pandas as pd
import chromadb

from utils.embedding_en import get_embedding

# chroma db
client = chromadb.PersistentClient(path="data/twpdp")
collection = client.get_or_create_collection("twpdp",metadata={"hnsw:space": "cosine"})

def load_into_chroma():
    twpdp = pd.read_csv('data/twpdp_dump.csv')

    twpdp_embeddings = []
    for twpdp_article in twpdp.iterrows():
        embeddings = None
        for _ in range(3): # max retry = 3
            embeddings = get_embedding(twpdp_article[1]['content'])
            # print(embeddings)
            if embeddings is not None:
                break
        twpdp_embeddings.append(embeddings)

    documents = [twpdp_article[1]['content'] for twpdp_article in twpdp.iterrows()]
    ids = [str(twpdp_article[1]['article']) for twpdp_article in twpdp.iterrows()]
    titles = [twpdp_article[1]['article'] for twpdp_article in twpdp.iterrows()]

    collection.add(
        documents=documents,
        ids=ids,
        embeddings=twpdp_embeddings,
        metadatas=[{'ids':id,'titles':title} for id, title in zip(ids, titles)]
    )

def search_twpdp(query, k=2):
    query_embedding = get_embedding(query)
    results = collection.query(query_embedding, n_results=k)
    return results
    '''
    "ids": [["86", "4"]],
    "distances": [[0.7912275654965328, 0.8645201393055186]],
    "metadatas": [
        [
            {
                "ids": "86",
                "titles": "Processing and public access to official documents",
            },
            {"ids": "4", "titles": "Definitions"},
        ]
    ],
    '''

def search_twpdp_formatted(query, k=2):
    results = search_twpdp(query, k)
    formatted_str = ""
    for i in range(k):
        formatted_str += f"台灣個人資料保護法 {results['metadatas'][0][i]['ids']} \n"
        formatted_str += f"Content {results['documents'][0][i]} \n"
    return formatted_str

if __name__ == "__main__":
    # load_into_chroma()
    result = search_twpdp_formatted('個資定義')
    print(result)