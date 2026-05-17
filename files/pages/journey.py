import os
import streamlit as st

st.set_page_config(page_title="Behind the Magic", page_icon="📖", layout="centered")

_base_css = os.path.join(os.path.dirname(__file__), "..", "styles", "base.css")
with open(_base_css) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;600&display=swap');

/* --- Variables --- */
:root {
    --toggle-bg:     #c8973a;
    --toggle-icon:   #0e1a40;
    --glow-soft:     rgba(200, 151, 58, 0.3);
    --glow-strong:   rgba(200, 151, 58, 0.8);
    --blue-dark:    #0e1a40;
    --blue-deeper:  #0a1230;
    --blue-mid:     #162040;
    --blue-accent:  #1a2a6c;
    --gold:         #c8973a;
    --gold-light:   #d4af37;
    --gold-bright:  #e8c94a;
    --text-main:    #dce8f0;
    --text-muted:   #a8c8e0;
    --text-warm:    #e8d5b0;
    --font-mono:    'JetBrains Mono', monospace;
    --font-sans:    'Inter', sans-serif;
}

/* --- Base --- */
.stApp {
    background-color: var(--blue-dark);
    color: var(--text-main);
}

/* --- Headings --- */
h1, h2, h3, th, code {
    font-family: var(--font-mono) !important;
}

h1 {
    color: var(--gold) !important;
    font-weight: 600;
    font-size: 1.9rem;
    margin-bottom: 0.25rem;
}

h2 {
    color: var(--text-muted) !important;
    font-weight: 600;
    font-size: 1.2rem;
    margin-top: 2rem;
    border-bottom: 1px solid #c8973a44;
    padding-bottom: 0.3rem;
}

h3 {
    color: var(--gold) !important;
    font-weight: 400;
    font-size: 1rem;
}

/* --- Body text --- */
p, li, td {
    font-family: var(--font-sans);
    font-size: 1.05rem;
    line-height: 1.85;
    color: var(--text-main);
}

em   { color: var(--text-muted); }
strong { color: var(--text-warm); }

/* --- Code --- */
code {
    background-color: var(--blue-mid);
    color: var(--gold);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.88rem;
}

pre {
    background-color: var(--blue-mid) !important;
    border: 1px solid #c8973a44;
    border-radius: 6px;
    padding: 1rem;
}

/* --- Blockquote & HR --- */
blockquote {
    border-left: 3px solid var(--gold);
    padding-left: 1.2rem;
    color: var(--text-muted);
    font-style: italic;
    margin: 1.5rem 0;
}

hr {
    border-color: var(--gold);
    opacity: 0.25;
    margin: 2rem 0;
}

/* --- Table --- */
table { width: 100%; border-collapse: collapse; }

th {
    background-color: var(--blue-mid);
    color: var(--gold);
    padding: 0.5rem 1rem;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #c8973a22;
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background-color: var(--blue-deeper) !important;
    border-right: 1px solid #c8973a33;
}


</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Navigation")
    st.page_link("hpexplorer.py", label="Home Page", icon="⚡")

journey_path = os.path.join(os.path.dirname(__file__), "..", "my-rag-journey.md")

if os.path.exists(journey_path):
    with open(journey_path, "r") as f:
        st.markdown(f.read())
else:
    st.error("Journey file not found.")
