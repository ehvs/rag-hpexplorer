THEMES = {
    "harrypotter": {
        "page_icon": "⚡",
        "title": "⚡ Local Library",
        "subtitle": "Upload your own book and make questions",
        "primary": "#d4af37",
        "bg": "#0d0d1a",
        "text": "#e8d5a3",
        "subtitle_color": "#9e8866",
        "input_bg": "#1a1a2e",
        "sidebar_bg": "#0a0a16",
        "answer_bg": "linear-gradient(135deg, #f5e6c8, #ede0b0)",
        "answer_text": "#2c1810",
        "answer_border": "#8b1a1a",
        "badge_bg": "#1a2a1a",
        "toggle_bg": "#d4af37",
        "toggle_icon": "#0d0d1a",
        "glow_soft": "rgba(212, 175, 55, 0.3)",
        "glow_strong": "rgba(212, 175, 55, 0.8)",
        "font_import": "@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Crimson+Text:ital,wght@0,400;1,400&display=swap');",
        "heading_font": "'Cinzel', serif",
        "body_font": "'Crimson Text', serif",
        "sidebar_title": "### 📜 The Restricted Section",
        "sidebar_intro": "*Welcome, young wizard.*",
        "sidebar_steps": "1. 📖 Upload a PDF tome to begin.\n2. 🦉 Cast your question to the Sorting Hat.\n3. ✨ Wisdom from the pages shall be revealed.",
        "sidebar_quote": '*"Hermione, when have any of our plans actually worked? We plan, we get there, everything goes wrong." 😂*',
        "sidebar_quote_author": "— Ron Weasley",
        "spinner_loading": "Consulting the ancient scrolls...",
        "spinner_thinking": "The Sorting Hat is thinking...",
        "question_label": "🪄 Cast your question:",
        "answer_icon": "📜",
        "no_file_msg": "No tome found in the restricted section. Please upload a document to begin.",
    },
    # Palette (strict): #faca16 #6cb4ee #f58553 #9a81b0 #669e63 #fc89ac #8e715b
    # Role mapping:
    #   #8e715b  bg             (darkest — base background)
    #   #669e63  sidebar_bg     (green sidebar)
    #   #9a81b0  input_bg       (purple inputs)
    #   #9a81b0  answer_bg      (purple answer box)
    #   #faca16  text           (yellow on dark)
    #   #faca16  answer_text
    #   #6cb4ee  primary        (blue — headings, borders, badge)
    #   #fc89ac  subtitle_color (pink)
    #   #f58553  answer_border  (orange accent stripe)
    #   #669e63  badge_bg       (green badge)
    #   #6cb4ee  toggle_bg
    #   #8e715b  toggle_icon
    "generic": {
        "page_icon": "📚",
        "title": "📚 Document Explorer",
        "subtitle": "Upload a document and ask questions",
        "primary": "#6cb4ee",
        "bg": "#8e715b",
        "text": "#faca16",
        "subtitle_color": "#fc89ac",
        "input_bg": "#9a81b0",
        "sidebar_bg": "#669e63",
        "answer_bg": "#9a81b0",
        "answer_text": "#faca16",
        "answer_border": "#f58553",
        "badge_bg": "#669e63",
        "toggle_bg": "#6cb4ee",
        "toggle_icon": "#8e715b",
        "glow_soft": "rgba(108, 180, 238, 0.3)",
        "glow_strong": "rgba(108, 180, 238, 0.8)",
        "font_import": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');",
        "heading_font": "'Inter', sans-serif",
        "body_font": "'Inter', sans-serif",
        "sidebar_title": "### 📋 How to use",
        "sidebar_intro": "*Welcome to Document Explorer.*",
        "sidebar_steps": "1. 📖 Upload a PDF document to begin.\n2. 💬 Type your question in the box.\n3. ✨ Get answers sourced from your document.",
        "sidebar_quote": '*"The goal of education is not to increase the amount of knowledge but to create the possibilities for a child to invent and discover."*',
        "sidebar_quote_author": "— Jean Piaget",
        "spinner_loading": "Loading your document...",
        "spinner_thinking": "Searching for an answer...",
        "question_label": "💬 Ask a question:",
        "answer_icon": "💡",
        "no_file_msg": "No document loaded. Please upload a PDF to begin.",
    },
}


def build_css(t: dict) -> str:
    return f"""
{t['font_import']}

:root {{
    --toggle-bg:   {t['toggle_bg']};
    --toggle-icon: {t['toggle_icon']};
    --glow-soft:   {t['glow_soft']};
    --glow-strong: {t['glow_strong']};
}}

.stApp {{
    background-color: {t['bg']};
    color: {t['text']};
}}

h1 {{
    font-family: {t['heading_font']} !important;
    color: {t['primary']} !important;
    text-align: center;
    text-shadow: 0 0 20px {t['glow_soft']};
}}

h2, h3 {{
    font-family: {t['heading_font']} !important;
    color: {t['primary']} !important;
}}

.subtitle {{
    text-align: center;
    color: {t['subtitle_color']};
    font-style: italic;
    font-family: {t['body_font']};
    font-size: 1.1rem;
    margin-bottom: 1rem;
}}

.stTextInput > div > div > input {{
    background-color: {t['input_bg']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['primary']} !important;
    border-radius: 8px !important;
}}

.parchment {{
    background: {t['answer_bg']};
    color: {t['answer_text']};
    border-radius: 12px;
    padding: 1.5rem 2rem;
    border-left: 5px solid {t['answer_border']};
    font-family: {t['body_font']};
    font-size: 1.15rem;
    line-height: 1.7;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    margin-top: 1rem;
}}

[data-testid="stSidebar"] {{
    background-color: {t['sidebar_bg']} !important;
    border-right: 1px solid {t['primary']}44;
}}

hr {{
    border-color: {t['primary']};
    opacity: 0.3;
}}

.stFileUploader {{
    border: 1px dashed {t['primary']} !important;
    border-radius: 8px;
    padding: 0.5rem;
}}

.loaded-badge {{
    background-color: {t['badge_bg']};
    border: 1px solid {t['primary']};
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: {t['primary']};
    font-family: {t['heading_font']};
    font-size: 0.9rem;
    text-align: center;
    margin-bottom: 1rem;
}}
"""
