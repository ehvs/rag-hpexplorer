# Hogwarts Library — RAG Application

A Retrieval-Augmented Generation (RAG) system deployed on Streamlit Community Cloud. Users upload any PDF and ask questions about it in natural language. The system retrieves the most relevant passages and generates a grounded answer using a hosted language model.

---

## How It Works

### The RAG Pipeline

RAG solves a fundamental limitation of language models: they only know what they were trained on. By combining a retrieval step with generation, the system can answer questions grounded in a specific document — a book, a contract, a research paper — without fine-tuning the model on it.

The pipeline has three stages:

1. **Ingest** — the uploaded PDF is loaded, split into semantically coherent chunks, and each chunk is converted into a vector embedding representing its meaning numerically. The result is stored in a FAISS vector index.
2. **Retrieve** — when a question is asked, the same embedding model converts the question into a vector and finds the most relevant chunks using similarity search.
3. **Generate** — the retrieved chunks are injected into a prompt alongside the question, and the language model produces an answer grounded exclusively in that context.

---

## AI & RAG Components

### Language Model — Llama 3.3 70B via Groq

The generative brain of the system. Llama 3.3 70B is Meta's open-weight instruction-tuned model, accessed through Groq's inference API. Groq runs models on custom LPU (Language Processing Unit) hardware, which delivers very low latency compared to GPU-based providers.

**Why Groq over alternatives:**
- **Speed** — Groq's LPU delivers tokens significantly faster than standard GPU inference, keeping the app feeling responsive.
- **Free tier** — 14,400 requests/day at no cost, sufficient for a personal app.
- **No infrastructure** — no local GPU, no Ollama process, no machine requirements. The API call goes out and the answer comes back. This is the right trade-off for a cloud-deployed app.
- **OpenAI-compatible** — integrates natively with LangChain via `langchain-groq`, requiring minimal code change from the original Ollama setup.

**Why Llama 3.3 70B over smaller options:**
A 70B model handles nuanced factual retrieval tasks more reliably than 7–8B models — it follows the "answer only from context" prompt instruction more consistently and produces better-structured responses. On Groq, the latency difference between 8B and 70B is smaller than it would be on a GPU server.

**LLM configuration:**
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=250,
)
```
- `temperature=0` — deterministic output. For factual retrieval from a document, creativity is a liability.
- `max_tokens=250` — enforces concise answers. Without a cap, the model tends to elaborate beyond what the context supports.

---

### Embedding Model — BAAI/bge-small-en-v1.5 via FastEmbed

Converts text into dense vector representations (embeddings). This model understands semantic meaning, so chunks about "Harry's closest friends" can be retrieved even if the query says "best companions".

**Why FastEmbed:**
FastEmbed runs models locally using ONNX Runtime — no PyTorch, no Transformers, no GPU. It downloads the model weights once and runs inference entirely in-process. This is critical for Streamlit Community Cloud, which has a 1GB RAM cap. The alternatives that were tried first both failed:
- **Local HuggingFace (`HuggingFaceEmbeddings`)** — requires PyTorch (2+ GB installed), immediately exceeds Streamlit Cloud's memory and disk limits.
- **HuggingFace Inference API (`HuggingFaceInferenceAPIEmbeddings`)** — makes HTTP calls to HF's free tier, which returned empty responses for this model intermittently. Unreliable for production use.

FastEmbed occupies ~130MB and runs deterministically in-process. It is the correct fit for a constrained cloud environment.

**Why bge-small over bge-large:**
The original version used `BAAI/bge-large-en-v1.5` (1024 dimensions, 1.3GB). Switching to `BAAI/bge-small-en-v1.5` (384 dimensions, ~130MB) was driven by the deployment constraint, not preference. For a single-document QA app where the user is asking about content they uploaded themselves, the retrieval quality difference between large and small is minimal in practice — the right chunks still get found.

---

### Vector Store — FAISS

Facebook AI Similarity Search (FAISS) stores all chunk embeddings and performs fast nearest-neighbour search at query time. The index is built in-memory from the uploaded PDF and cached using `@st.cache_resource` with the MD5 hash of the PDF bytes as the cache key — uploading the same file twice skips re-processing.

**Why FAISS over managed alternatives (Pinecone, Qdrant Cloud, Chroma):**
FAISS requires no server, no account, no API key, and no network call at query time. It is a library, not a service. For a single-document app with thousands of chunks (not millions), it is more than fast enough. The only trade-off is that the index lives in memory and is lost on container restart — but for a personal upload-and-ask app, rebuilding from the uploaded file is acceptable. If this app were to grow into a multi-document persistent knowledge base, a hosted vector store would be the right next step.

---

### Chunking — SemanticChunker

Instead of splitting documents into fixed-size character blocks, SemanticChunker uses the embedding model to detect natural topic boundaries in the text. It computes the semantic distance between consecutive sentences and splits where the meaning shifts significantly.

**Why semantic chunking over fixed-size:**
Fixed-size chunking (e.g. every 500 characters) is fast and simple but splits text at arbitrary points — mid-sentence, mid-paragraph, mid-argument. A chunk that starts in the middle of a conversation has no context for retrieval. Semantic chunking produces chunks that are self-contained units of meaning, which retrieves better because each chunk accurately represents one idea.

The trade-off is speed: SemanticChunker calls the embedding model on every sentence boundary during index building. With FastEmbed running locally, this is slower than fixed chunking but still completes in a reasonable time for book-length PDFs.

---

### Retrieval Strategy — MMR (Maximum Marginal Relevance)

Standard similarity search returns the top-k most similar chunks, which can be redundant — five chunks all repeating the same passage about a character doesn't help the model answer a nuanced question. MMR balances relevance with diversity: it retrieves a larger candidate pool, then selects the subset that is both relevant to the query and maximally different from each other.

**Retriever configuration:**
```python
retriever = vectordb.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 15}
)
```

- `fetch_k=15` — FAISS first retrieves 15 candidates by similarity score. This is the raw pool before diversity filtering.
- `k=5` — MMR selects the 5 chunks that best balance relevance and variety. These are passed to the LLM as context.
- The 3:1 ratio between `fetch_k` and `k` is intentional. Too close (e.g. `fetch_k=6`) and MMR has almost nothing to diversify from; too far (e.g. `fetch_k=100`) and the extra candidates are wasted computation.

---

### Orchestration — LangChain

LangChain wires the retriever, prompt template, and LLM into a single callable chain using the LCEL (LangChain Expression Language) pipe syntax.

```python
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

The chain handles context formatting, prompt rendering, LLM invocation, and output parsing in one `chain.invoke(question)` call. LangChain was chosen because it provides the retriever abstraction, FAISS integration, and chain composition out of the box — replacing any component (e.g. swapping FAISS for Pinecone, or Groq for another provider) requires changing one line.

---

### Prompt Design

```
Use the following context to answer the question at the end.
If you don't know the answer, just say "I don't know" — do not make up an answer.
Answer directly and concisely in 1 paragraph maximum. You may draw reasonable
inferences from the context, but do not invent facts. This is a rule.
Respond in the same language as the question.

Context:
{context}

Question: {question}

Answer:
```

- **"Do not make up an answer"** — the most important instruction. Without it, the model will hallucinate plausible-sounding content when the retrieved context is insufficient.
- **"1 paragraph maximum"** — without a length constraint, the model elaborates beyond what the context supports. Short answers from retrieved context are almost always more accurate than long ones.
- **"Respond in the same language as the question"** — supports multilingual use without changing any other part of the system.

---

## Infrastructure

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11 | Pinned via `.python-version`; 3.12+ breaks several C-extension packages on Streamlit Cloud |
| UI & hosting | Streamlit Community Cloud | Zero-config deployment from a GitHub repo; free tier |
| LLM | Groq API — Llama 3.3 70B | Fast, free tier, no local GPU required |
| Embeddings | FastEmbed — bge-small-en-v1.5 | Runs locally via ONNX, no PyTorch, fits in 1GB RAM |
| Vector store | FAISS (in-memory) | No server needed, sufficient for single-document use |
| Chunking | SemanticChunker (LangChain) | Topic-aware splits produce better retrieval than fixed-size |
| Retrieval | MMR, k=5, fetch_k=15 | Reduces redundant context passed to the LLM |
| Orchestration | LangChain 0.3.x | Retriever abstraction, FAISS integration, chain composition |
| PDF processing | pdfplumber + pdfminer.six | Reliable text extraction from real-world PDFs |

---

## Key Design Decisions

- **Cloud-first** — the original version ran entirely locally (Ollama, local embeddings, local FAISS). The migration to Streamlit Community Cloud required replacing every local component with something that fits in 1GB RAM and requires no local process.
- **FastEmbed over API embeddings** — embedding via an external API (HuggingFace Inference API) introduced network unreliability and rate limits. Running ONNX locally is slower to start but reliable on every request.
- **User-uploaded PDFs** — the original app bundled Harry Potter and the Philosopher's Stone. Distributing a copyrighted book in a public repository is not appropriate. The app now accepts any PDF the user provides.
- **In-memory FAISS** — on Streamlit Community Cloud the filesystem is ephemeral. Rather than fighting this, the index is cached in-process via `@st.cache_resource`. For a single-user personal app, rebuilding from an upload is acceptable on container restart.
- **MMR over pure similarity** — reduces contradictory or redundant context that causes the model to hedge, repeat itself, or blend information from overlapping passages.
- **Prompt constraints** — enforcing a 1-paragraph maximum and "do not invent facts" significantly reduces hallucination on retrieved-context tasks, where the model's prior knowledge can interfere with document-grounded answers.
