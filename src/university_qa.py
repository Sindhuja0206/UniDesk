from groq import Groq
import os
from dotenv import load_dotenv
from src.gitam_retriever import retrieve_gitam

load_dotenv()

client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(question: str, chunks: list[dict]) -> str:
    context = ""
    for i, chunk in enumerate(chunks):
        context += f"\n[{i+1}] (Page {chunk['page']})\n{chunk['text']}\n"

    return f"""You are a helpful GITAM university information assistant.
Answer the student's question using ONLY the context below, which is extracted from the official
GITAM R24UG Academic Regulations document.
Always cite the sources you used inline using [1], [2] etc. right after the relevant sentence.
If the answer is not in the context, say "This information is not available in the provided GITAM
academic regulations. Please contact the university directly."

Context:
{context}

Question: {question}

Answer:"""


def ask_university(question: str) -> tuple[str, str]:
    """Answer a GITAM-related question using RAG over the ingested regulations PDF."""
    chunks = retrieve_gitam(question, top_k=5)

    if not chunks:
        return (
            "No GITAM regulations data found. Please ask the admin to ingest the GITAM PDF first.",
            ""
        )

    prompt = build_prompt(question, chunks)

    response = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )

    answer = response.choices[0].message.content

    seen_pages = []
    sources_lines = []
    for i, chunk in enumerate(chunks):
        page = chunk["page"]
        sources_lines.append(f"[{i+1}] GITAM Academic Regulations — Page {page}")
        if page not in seen_pages:
            seen_pages.append(page)

    sources = "\n".join(sources_lines)
    return answer, sources