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
from themes import THEMES, build_css

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
ACTIVE_THEME = "generic"  # toggle: "harrypotter" | "generic"

t = THEMES[ACTIVE_THEME]

st.set_page_config(page_title=t["title"], page_icon=t["page_icon"], layout="centered")

with open(os.path.join(SCRIPT_DIR, "styles", "base.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(f"<style>{build_css(t)}</style>", unsafe_allow_html=True)

st.title(t["title"])
st.markdown(f'<p class="subtitle">{t["subtitle"]}</p>', unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown(t["sidebar_title"])
    st.markdown(f"\n{t['sidebar_intro']}\n\n{t['sidebar_steps']}\n")
    st.markdown("---")
    st.markdown("📖 **Curious how this was built?**")
    st.page_link("pages/journey.py", label="Read about my journey", icon="✨")
    st.markdown("---")
    st.markdown(t["sidebar_quote"])
    st.markdown(t["sidebar_quote_author"])


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
    with st.spinner(t["spinner_loading"]):
        qa_chain = build_qa_chain(file_bytes)

    st.markdown(f'<div class="loaded-badge">📖 {label}</div>', unsafe_allow_html=True)

    user_input = st.text_input(t["question_label"])

    if user_input:
        logger.info(f"User question: {user_input}")
        with st.spinner(t["spinner_thinking"]):
            try:
                response = qa_chain.invoke(user_input)
                if SHOW_DEBUG:
                    with st.expander("🔍 Debug info"):
                        st.write(f"Response type: `{type(response)}`")
                        st.code(repr(response))
                if response and response.strip():
                    st.markdown(f'<div class="parchment">{t["answer_icon"]} {response}</div>', unsafe_allow_html=True)
                else:
                    logger.warning("Empty response returned to user")
                    st.warning("No answer found. Try rephrasing your question.")
            except Exception as e:
                logger.error(f"Chain error: {e}")
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())
else:
    st.info(t["no_file_msg"])
