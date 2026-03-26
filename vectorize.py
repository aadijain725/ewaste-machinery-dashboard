#!/usr/bin/env python3
"""Generate vector embeddings for semantic search over e-waste data.

Requires: pip install sentence-transformers numpy

Usage:
    python vectorize.py           # Generate embeddings
    python vectorize.py search "copper recovery machines"   # Semantic search
"""

import sqlite3
import struct
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ewaste.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_to_blob(embedding):
    """Pack a numpy array into a BLOB for SQLite storage."""
    return struct.pack(f"{len(embedding)}f", *embedding.tolist())


def blob_to_embed(blob):
    """Unpack a BLOB back into a list of floats."""
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def cosine_sim(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def generate_embeddings():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = load_model()
    conn = get_db()
    cur = conn.cursor()

    texts = []
    metadata = []

    # Categories
    for row in cur.execute("SELECT * FROM categories"):
        text = f"{row['name']}: {row['full_name']}. {row['items']}. {row['notes']}"
        texts.append(text)
        metadata.append(("category", row["id"], f"{row['name']}: {row['full_name']}"))

    # Machines
    for row in cur.execute("SELECT * FROM machines ORDER BY id"):
        text = f"Machine #{row['id']}: {row['name']}. {row['description']}. {row['specs']}"
        texts.append(text)
        metadata.append(("machine", str(row["id"]), f"#{row['id']} {row['name']}"))

    # Configurations
    for row in cur.execute("SELECT * FROM configurations"):
        text = f"{row['name']}: {row['display_name']}. {row['description']}"
        texts.append(text)
        metadata.append(("configuration", row["id"], f"{row['name']}: {row['display_name']}"))

    print(f"Encoding {len(texts)} items...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # Store in DB
    cur.execute("DELETE FROM embeddings")
    for i, (etype, eid, title) in enumerate(metadata):
        cur.execute(
            "INSERT INTO embeddings (entity_type, entity_id, text, embedding, model) VALUES (?,?,?,?,?)",
            (etype, eid, texts[i], embed_to_blob(embeddings[i]), "all-MiniLM-L6-v2"))

    conn.commit()
    conn.close()
    print(f"Stored {len(texts)} embeddings in {DB_PATH}")


def semantic_search(query, top_k=10):
    model = load_model()
    query_emb = model.encode([query])[0]

    conn = get_db()
    rows = conn.execute("SELECT * FROM embeddings").fetchall()

    results = []
    for row in rows:
        emb = blob_to_embed(row["embedding"])
        sim = cosine_sim(query_emb, emb)
        results.append({
            "type": row["entity_type"],
            "id": row["entity_id"],
            "text": row["text"][:200],
            "score": sim,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    conn.close()
    return results[:top_k]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:])
        if not query:
            print("Usage: python vectorize.py search '<query>'")
            exit(1)
        results = semantic_search(query)
        print(f"\nSemantic search: \"{query}\"\n")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['type']}] {r['text'][:100]}...")
            print(f"     Score: {r['score']:.4f}\n")
    else:
        generate_embeddings()
