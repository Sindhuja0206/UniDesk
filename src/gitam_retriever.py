import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

client = chromadb.PersistentClient(path="./vectorstore")
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
gitam_collection = client.get_or_create_collection("gitam_docs", embedding_function=embedding_fn)


def retrieve_gitam(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve relevant chunks from the GITAM Academic Regulations collection."""
    results = gitam_collection.query(query_texts=[query], n_results=top_k)

    if not results["documents"] or not results["documents"][0]:
        return []

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "page": results["metadatas"][0][i]["page"],
        })
    return chunks