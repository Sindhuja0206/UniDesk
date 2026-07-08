import os
import fitz
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

client = chromadb.PersistentClient(path="./vectorstore")
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection("syllabus_docs", embedding_function=embedding_fn)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append({"text": text, "page": page_num + 1})
    return pages

def ingest_pdf(pdf_path: str):
    filename = os.path.basename(pdf_path)
    print(f"[INGEST] Ingesting: {filename}")
    pages = extract_text_from_pdf(pdf_path)
    all_chunks, all_ids, all_metadata = [], [], []
    for page_data in pages:
        chunks = splitter.split_text(page_data["text"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}_p{page_data['page']}_c{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadata.append({
                "source": filename,
                "page": page_data["page"]
            })
    collection.add(documents=all_chunks, ids=all_ids, metadatas=all_metadata)
    print(f"   [OK] {len(all_chunks)} chunks stored from {filename}")

def ingest_all_pdfs(pdf_folder: str = "./data/pdfs"):
    pdfs = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    if not pdfs:
        print("No PDFs found in ./data/pdfs")
        return
    for pdf in pdfs:
        ingest_pdf(os.path.join(pdf_folder, pdf))
    print(f"\n[DONE] {len(pdfs)} PDFs ingested.")

if __name__ == "__main__":
    ingest_all_pdfs()