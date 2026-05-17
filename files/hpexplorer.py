# RAG System - Hogwarts Library

# Imports
import os
import hashlib
import logging
import tempfile
import warnings
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
logger.propagate = False

GROQ_MODEL = "llama-3.3-70b-versatile"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHOW_UPLOADER = True
SHOW_DEBUG = False

st.set_page_config(page_title="Local Library", page_icon="⚡", layout="centered")

with open(os.path.join(SCRIPT_DIR, "styles", "base.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Crimson+Text:ital,wght@0,400;1,400&display=swap');

:root {
    --toggle-bg:     #d4af37;
    --toggle-icon:   #0d0d1a;
    --glow-soft:     rgba(212, 175, 55, 0.3);
    --glow-strong:   rgba(212, 175, 55, 0.8);
}

.stApp {
    background-color: #0d0d1a;
    color: #e8d5a3;
}

h1 {
    font-family: 'Cinzel', serif !important;
    color: #d4af37 !important;
    text-align: center;
    text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
}

h2, h3 {
    font-family: 'Cinzel', serif !important;
    color: #d4af37 !important;
}

.subtitle {
    text-align: center;
    color: #9e8866;
    font-style: italic;
    font-family: 'Crimson Text', serif;
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.stTextInput > div > div > input {
    background-color: #1a1a2e !important;
    color: #e8d5a3 !important;
    border: 1px solid #d4af37 !important;
    border-radius: 8px !important;
}

.parchment {
    background: linear-gradient(135deg, #f5e6c8, #ede0b0);
    color: #2c1810;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    border-left: 5px solid #8b1a1a;
    font-family: 'Crimson Text', serif;
    font-size: 1.15rem;
    line-height: 1.7;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    margin-top: 1rem;
}

[data-testid="stSidebar"] {
    background-color: #0a0a16 !important;
    border-right: 1px solid #d4af3744;
}

hr {
    border-color: #d4af37;
    opacity: 0.3;
}

.stFileUploader {
    border: 1px dashed #d4af37 !important;
    border-radius: 8px;
    padding: 0.5rem;
}

.loaded-badge {
    background-color: #1a2a1a;
    border: 1px solid #d4af37;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #d4af37;
    font-family: 'Cinzel', serif;
    font-size: 0.9rem;
    text-align: center;
    margin-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)

st.title("⚡ Hogwarts Library")
st.markdown('<p class="subtitle">Upload your own book and make questions</p>', unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("### 📜 The Restricted Section")
    st.markdown("""
*Welcome, young wizard.*

1. 📖 Upload a PDF tome to begin.
2. 🦉 Cast your question to the Sorting Hat.
3. ✨ Wisdom from the pages shall be revealed.
    """)
    st.markdown("---")
    st.markdown("📖 **Curious how this was built?**")
    st.page_link("pages/journey.py", label="Read about my journey", icon="✨")
    st.markdown("---")
    st.markdown("*\"Hermione, when have any of our plans actually worked? We plan, we get there, everything goes wrong.\"*  😂")
    st.markdown("— Ron Wesley")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


@st.cache_resource(show_spinner=False)
def build_qa_chain(file_bytes: bytes):
    file_hash = hashlib.md5(file_bytes).hexdigest()
    index_path = os.path.join(SCRIPT_DIR, f"faiss_index_{file_hash}")

    embedder = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    if os.path.exists(index_path):
        logger.info(f"FAISS index cache hit: {index_path}")
        vectordb = FAISS.load_local(index_path, embedder, allow_dangerous_deserialization=True)
    else:
        logger.info("FAISS index not found — building from PDF")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            loader = PDFPlumberLoader(tmp_path)
            docs = loader.load()
        finally:
            os.unlink(tmp_path)

        if not docs:
            raise ValueError("No extractable text found in this PDF. Is it a scanned image?")

        text_splitter = SemanticChunker(embedder)
        documents = text_splitter.split_documents(docs)

        vectordb = FAISS.from_documents(documents, embedder)
        vectordb.save_local(index_path)

    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 15})

    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        max_tokens=250,
        api_key=st.secrets["GROQ_API_KEY"],
    )

    prompt = PromptTemplate.from_template("""Use the following context to answer the question at the end.
If you don't know the answer, just say "I don't know" — do not make up an answer.
Answer directly and concisely in 1 paragraph maximum. You may draw reasonable inferences from the context, but do not invent facts. This is a rule.
Respond in the same language as the question.

Context:
{context}

Question: {question}

Answer:""")

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


DEFAULT_PDF = os.path.join(SCRIPT_DIR, "hp-and-the-philosophers-stone.pdf")

uploaded_file = st.file_uploader("Upload a different tome (optional)", type="pdf") if SHOW_UPLOADER else None

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    label = uploaded_file.name
elif os.path.exists(DEFAULT_PDF):
    with open(DEFAULT_PDF, "rb") as f:
        file_bytes = f.read()
    label = "Harry Potter and the Philosopher's Stone"
else:
    file_bytes = None
    label = None

if file_bytes is not None:
    with st.spinner("Consulting the ancient scrolls..."):
        qa_chain = build_qa_chain(file_bytes)

    st.markdown(f'<div class="loaded-badge">📖 {label}</div>', unsafe_allow_html=True)

    user_input = st.text_input("🪄 Cast your question:")

    if user_input:
        logger.info(f"User question: {user_input}")
        with st.spinner("The Sorting Hat is thinking..."):
            try:
                response = qa_chain.invoke(user_input)
                if SHOW_DEBUG:
                    with st.expander("🔍 Debug info"):
                        st.write(f"Response type: `{type(response)}`")
                        st.code(repr(response))
                if response and response.strip():
                    st.markdown(f'<div class="parchment">📜 {response}</div>', unsafe_allow_html=True)
                else:
                    logger.warning("Empty response returned to user")
                    st.warning("The Sorting Hat returned silence. Try rephrasing your question.")
            except Exception as e:
                logger.error(f"Chain error: {e}")
                st.error(f"A dark spell interfered: {e}")
                import traceback
                st.code(traceback.format_exc())
else:
    st.info("No tome found in the restricted section. Please upload a document to begin.")
