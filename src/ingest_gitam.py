import os
import fitz
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

client = chromadb.PersistentClient(path="./vectorstore")
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

gitam_collection = client.get_or_create_collection("gitam_docs", embedding_function=embedding_fn)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def ingest_gitam_pdf(pdf_path: str = "./data/university_pdfs/gitam.pdf"):
    """Ingest the GITAM Academic Regulations PDF into its own ChromaDB collection."""
    if not os.path.exists(pdf_path):
        return f"❌ GITAM PDF not found at {pdf_path}"

    filename = os.path.basename(pdf_path)
    print(f"[INGEST] Ingesting: {filename}")

    doc = fitz.open(pdf_path)
    all_chunks, all_ids, all_metadata = [], [], []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        if not text.strip():
            continue
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}_p{page_num+1}_c{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadata.append({
                "source": filename,
                "page": page_num + 1
            })

    if all_chunks:
        existing = gitam_collection.get()
        if existing["ids"]:
            gitam_collection.delete(ids=existing["ids"])

        gitam_collection.add(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadata
        )
        print(f"   [OK] {len(all_chunks)} chunks stored")
        return f"✅ GITAM regulations ingested successfully! ({len(all_chunks)} chunks, {len(doc)} pages)"

    return "⚠️ No text could be extracted from the PDF."


if __name__ == "__main__":
    print(ingest_gitam_pdf())