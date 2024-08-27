import pandas as pd
import chromadb

from utils.embedding_en import get_embedding

# chroma db
client = chromadb.PersistentClient(path="data/gdpr")
collection = client.get_or_create_collection("gdpr",metadata={"hnsw:space": "cosine"})

def load_into_chroma():
    gdpr = pd.read_excel('data/GDPR_dump.xlsx')
    gdpr = gdpr[gdpr['Type'] == 'Article']

    gdpr_embeddings = []
    for gdpr_article in gdpr.iterrows():
        embeddings = None
        for _ in range(3): # max retry = 3
            embeddings = get_embedding(gdpr_article[1]['Content_Items'])
            # print(embeddings)
            if embeddings is not None:
                break
        gdpr_embeddings.append(embeddings)

    documents = [gdpr_article[1]['Content_Items'] for gdpr_article in gdpr.iterrows()]
    ids = [str(gdpr_article[1]['Text']) for gdpr_article in gdpr.iterrows()]
    titles = [gdpr_article[1]['Title'] for gdpr_article in gdpr.iterrows()]

    collection.add(
        documents=documents,
        ids=ids,
        embeddings=gdpr_embeddings,
        metadatas=[{'ids':id,'titles':title} for id, title in zip(ids, titles)]
    )

def search_gdpr(query, k=2):
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

def search_gdpr_formatted(query, k=2):
    results = search_gdpr(query, k)
    formatted_str = ""
    for i in range(k):
        formatted_str += f"Article {results['metadatas'][0][i]['ids']} \n"
        formatted_str += f"Title {results['metadatas'][0][i]['titles']} \n"
        formatted_str += f"Content {results['documents'][0][i]} \n"
    return formatted_str

if __name__ == "__main__":
    result = search_gdpr_formatted('‘personal data’ means any information relating to an identified or identifiable natural person')
    print(result)