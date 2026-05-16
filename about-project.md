# Hogwarts Library — RAG Application

A local Retrieval-Augmented Generation (RAG) system built around Harry Potter and the Philosopher's Stone, running entirely on local infrastructure without external AI APIs.

---

## How It Works

### The RAG Pipeline

RAG solves a fundamental limitation of language models: they only know what they were trained on. By combining a retrieval step with generation, the system can answer questions grounded in a specific document — in this case, a book the model has never been fine-tuned on.

The pipeline has three stages:

1. **Ingest** — the PDF is loaded, split into semantic chunks, and each chunk is converted into a vector embedding representing its meaning numerically.
2. **Retrieve** — when a question is asked, the same embedding model converts the question into a vector and finds the most relevant chunks using similarity search.
3. **Generate** — the retrieved chunks are injected into a prompt alongside the question, and the language model generates an answer grounded in that context.

---

## AI & RAG Components

### Language Model — Qwen 3.5 9B via Ollama
The generative brain of the system. Qwen 3.5 is a 9-billion parameter instruction-tuned model running locally through Ollama. It receives the retrieved context and the user's question, and produces a concise answer. Thinking mode is explicitly disabled (`think=False`) to skip internal chain-of-thought reasoning and reduce latency.

### Embedding Model — BAAI/bge-large-en-v1.5
Converts text into dense vector representations (embeddings). This model is one of the strongest open-source options for retrieval tasks — it understands semantic meaning, so chunks about "Harry's companions" can be retrieved even if the query says "best friends". Embeddings are computed once and cached on disk.

### Vector Store — FAISS
Facebook AI Similarity Search (FAISS) stores all chunk embeddings and performs fast nearest-neighbour search at query time. The index is persisted locally using an MD5 hash of the PDF as the cache key, so re-uploading the same file skips re-processing entirely.

**Why FAISS over alternatives (Chroma, Qdrant, Pinecone):**
FAISS was chosen for simplicity and fit. It requires no server, no Docker container, and no external service — it's just files on disk. For a single book with thousands of chunks (not millions), FAISS is more than fast enough. It also integrates with LangChain out of the box with minimal configuration. It was the right tool to get started without friction. If the app were to grow — multiple books, concurrent users, cloud deployment — Chroma or Qdrant would be worth the switch.

### Chunking — SemanticChunker
Instead of splitting the book into fixed-size character blocks, SemanticChunker uses the embedding model to detect natural topic boundaries in the text. This produces chunks that are semantically coherent — a chunk about the Sorting Hat ceremony won't be split mid-sentence across two chunks about different topics.

### Retrieval Strategy — MMR (Maximum Marginal Relevance)
Standard similarity search returns the top-k most similar chunks, which can be redundant or contradictory (e.g. two chunks both mentioning "Stonewall High" and "Hogwarts"). MMR balances relevance with diversity — it fetches a larger candidate pool and selects chunks that are relevant to the query but different from each other, reducing noise in the context window.

**Retriever configuration:**
```python
retriever = vectordb.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 15}
)
```

- `search_type="mmr"` — uses Maximum Marginal Relevance instead of pure cosine similarity. Pure similarity can return 5 chunks that all say the same thing; MMR ensures variety.
- `fetch_k=15` — FAISS first retrieves 15 candidate chunks by similarity score. This is the raw pool before diversity filtering is applied.
- `k=5` — from those 15 candidates, MMR selects the 5 that best balance relevance to the question and difference from each other. These 5 are what gets passed to the LLM as context.

The ratio between `fetch_k` and `k` matters: too close together (e.g. `k=5, fetch_k=6`) and MMR has almost no candidates to diversify from; too far apart (e.g. `k=5, fetch_k=100`) and you're wasting compute retrieving chunks that will never be used. A 3:1 ratio (`fetch_k` = 3× `k`) is a practical starting point.

### Orchestration — LangChain
LangChain wires the retriever, prompt template, and LLM into a single callable chain. The chain handles context formatting, prompt rendering, and passing the result through the Ollama call in one `invoke()`.

---

## Infrastructure

| Layer | Technology |
|---|---|
| Language | Python 3.13 (conda) |
| UI | Streamlit |
| LLM runtime | Ollama |
| LLM model | Qwen 3.5 9B |
| Embeddings | BAAI/bge-large-en-v1.5 (HuggingFace) |
| Vector store | FAISS (local, persisted) |
| Orchestration | LangChain |
| Public tunnel | ngrok |

---

## Key Design Decisions

- **Fully local** — no data leaves the machine. The LLM, embeddings, and vector store all run on-device.
- **Cached indexing** — the FAISS index is saved to disk after the first build. Subsequent loads are near-instant.
- **MMR over pure similarity** — reduces contradictory context that causes the model to hedge or hallucinate.
- **`think=False`** — disables Qwen's internal reasoning chain to cut response latency without affecting answer quality for factual retrieval tasks.
- **Prompt constraints** — the system prompt enforces a 1-paragraph maximum and instructs the model to draw only from the provided context, keeping answers grounded and concise.
