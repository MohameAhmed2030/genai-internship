import os
import math
import json
from openai import OpenAI

client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

INDEX_FILE = "rag_index.json"
DOC_FILE = "sample_doc.txt"
HISTORY_FILE = "chat_history.json"

# ===============================
# Load Document
# ===============================
def load_text_file(path: str) -> str:
    cwd = os.getcwd()
    full_path = path if os.path.isabs(path) else os.path.join(cwd, path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


# ===============================
# Chunk Text
# ===============================
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += step

    return chunks


# ===============================
# Embeddings
# ===============================
def embed_texts(texts):
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [d.embedding for d in resp.data]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))

    if na == 0 or nb == 0:
        return 0.0

    return dot / (na * nb)


# ===============================
# Build + Save Index
# ===============================
def build_index(chunks):
    print("Creating embeddings...")
    vectors = embed_texts(chunks)

    return [
        {"id": i, "text": c, "vec": v}
        for i, (c, v) in enumerate(zip(chunks, vectors))
    ]


def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f)
    print("Index saved ✅")


def load_index():
    if not os.path.exists(INDEX_FILE):
        return None

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        print("Index loaded ✅")
        return json.load(f)


# ===============================
# Retrieval
# ===============================
def retrieve_top_k(index, question, k=3):
    q_vec = embed_texts([question])[0]

    scored = []
    for item in index:
        score = cosine_similarity(q_vec, item["vec"])
        scored.append((score, item["id"], item["text"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


# ===============================
# Chat Memory RAG Answer
# ===============================
def answer_with_memory_rag(question, top_chunks, history):

    # Step 7 — Memory trimming (keep last 20 messages max)
    if len(history) > 20:
        history = history[-20:]

    context = "\n\n---\n\n".join([txt for _, _, txt in top_chunks])

    system_message = {
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "Use ONLY the provided document context. "
            "If the answer is not in the context, say you don't know."
        )
    }

    context_message = {
        "role": "system",
        "content": f"DOCUMENT CONTEXT:\n{context}"
    }

    messages = [system_message, context_message]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        max_tokens=300,
        temperature=0.3   # Step 9 — Controlled factual output
    )

    return resp.choices[0].message.content


# ===============================
# Chat History Persistence
# ===============================
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":

    print("Current folder:", os.getcwd())

    index = load_index()

    if index is None:
        print("No index found. Building new index...")
        text = load_text_file(DOC_FILE)
        chunks = chunk_text(text)
        index = build_index(chunks)
        save_index(index)

    print("\n🧠 Chat‑Style Memory RAG Ready 🚀")
    print("Type 'reset' to clear memory.")
    print("Type 'exit' to quit.")

    history = load_history()

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            break

        # Step 6 — Reset memory command
        if question.lower() == "reset":
            history = []
            save_history(history)
            print("Memory cleared ✅")
            continue

        top_chunks = retrieve_top_k(index, question, k=3)

        print("Top similarity scores:",
              [round(score, 3) for score, _, _ in top_chunks])

        answer = answer_with_memory_rag(question, top_chunks, history)

        print("\n🤖 Assistant:\n", answer)

        print("\nSources used:")
        for score, cid, _ in top_chunks:
            print(f"- Chunk {cid} (score: {round(score, 3)})")

        # Save conversation memory
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        save_history(history)