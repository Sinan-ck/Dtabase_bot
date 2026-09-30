"""Streamlit chat UI for the Text-to-SQL bot.

Flow: question -> find similar examples (FAISS) -> Llama writes SQL
      -> run on MySQL -> Llama explains the result.

Run with:  streamlit run streamlit_app.py
"""

import os
import re
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import text
from langchain_core.documents import Document
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from examples import EXAMPLES

load_dotenv()

st.set_page_config(page_title="Database Bot", page_icon="🗄️", layout="wide")

# ------------------------------------------------------------
# Settings (from .env, with defaults)
# ------------------------------------------------------------
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "atliq_tshirts")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


# ------------------------------------------------------------
# Load heavy things once (cached across reruns)
# ------------------------------------------------------------
@st.cache_resource(show_spinner="Connecting to MySQL...")
def get_db():
    return SQLDatabase.from_uri(
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}",
        sample_rows_in_table_info=3,
    )


@st.cache_resource(show_spinner="Loading Ollama model...")
def get_llm():
    return ChatOllama(model=OLLAMA_MODEL, temperature=0)


@st.cache_resource(show_spinner="Building example search index...")
def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    docs = [
        Document(page_content=ex["question"], metadata={"sql": ex["sql"]})
        for ex in EXAMPLES
    ]
    return FAISS.from_documents(docs, embedding=embeddings)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace)\b",
    re.IGNORECASE,
)


def clean_sql(raw: str) -> str:
    """Remove markdown fences the model may add."""
    return raw.replace("```sql", "").replace("```", "").strip()


def is_safe_select(sql: str) -> bool:
    """Allow one read-only SELECT/WITH statement only."""
    body = sql.strip().rstrip(";")
    if ";" in body:
        return False
    if not body.upper().startswith(("SELECT", "WITH")):
        return False
    return not FORBIDDEN.search(body)


def build_prompt(question: str, schema: str, similar_docs) -> str:
    examples_text = ""
    for doc in similar_docs:
        examples_text += (
            f"\nExample Question:\n{doc.page_content}\n"
            f"Example SQL:\n{doc.metadata['sql']}\n"
        )

    return f"""You are an expert MySQL Text-to-SQL assistant.
Your job is to write a correct MySQL query.

DATABASE SCHEMA:
{schema}

Here are some similar question and SQL examples:
{examples_text}

IMPORTANT RULES:
1. Use only tables and columns that exist in the schema.
2. Follow the SQL patterns from the examples when they are relevant.
3. Do not invent columns.
4. Use JOIN when information comes from multiple tables.
5. Return ONLY the SQL query.
6. Do not explain the query.
7. Do not use markdown code fences.

USER QUESTION:
{question}
"""


def answer_question(question: str) -> dict:
    """Run the full pipeline and return every step for display."""
    db, llm, vectorstore = get_db(), get_llm(), get_vectorstore()

    similar = vectorstore.similarity_search(question, k=3)
    prompt = build_prompt(question, db.get_table_info(), similar)
    sql = clean_sql(llm.invoke(prompt).content)

    out = {"similar": similar, "sql": sql, "df": None, "answer": None, "error": None}

    if not is_safe_select(sql):
        out["error"] = (
            "The model did not return a single read-only SELECT query, "
            "so nothing was run. Try rephrasing your question."
        )
        return out

    try:
        with db._engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
    except Exception as exc:  # show SQL errors in the UI instead of crashing
        out["error"] = f"MySQL returned an error: {exc}"
        return out

    out["df"] = df

    answer_prompt = f"""Question:
{question}

SQL:
{sql}

Database result:
{df.to_string(index=False)}

Give the answer in one short, clear sentence.
Do not invent information.
Use only the database result."""
    out["answer"] = llm.invoke(answer_prompt).content.strip()
    return out


def render_result(res: dict) -> None:
    """Show one pipeline result."""
    if res["error"]:
        st.error(res["error"])
    else:
        st.success(res["answer"])
        st.dataframe(res["df"], use_container_width=True, hide_index=True)

    with st.expander("Generated SQL", expanded=bool(res["error"])):
        st.code(res["sql"], language="sql")

    with st.expander("Similar examples used"):
        for i, doc in enumerate(res["similar"], start=1):
            st.markdown(f"**{i}. {doc.page_content}**")
            st.code(doc.metadata["sql"], language="sql")


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
with st.sidebar:
    st.header("Database")
    try:
        db = get_db()
        st.write(f"**{DB_NAME}** on `{DB_HOST}`")
        st.write("Tables:", ", ".join(db.get_usable_table_names()))
        with st.expander("Schema"):
            st.code(db.get_table_info(), language="sql")
    except Exception as exc:
        st.error(f"Cannot connect to MySQL: {exc}")
        st.stop()

    st.header("Try a question")
    samples = [
        "How many t-shirts are in stock in total?",
        "Rank all brands by their total inventory value from highest to lowest.",
        "Which brand has the highest total discount savings?",
        "Find the color with the highest total stock quantity.",
    ]
    for s in samples:
        if st.button(s, use_container_width=True):
            st.session_state["pending_question"] = s

    if st.button("Clear chat", use_container_width=True):
        st.session_state["history"] = []
        st.rerun()

# ------------------------------------------------------------
# Main chat area
# ------------------------------------------------------------
st.title("🗄️ Database Bot")
st.caption("Ask a question in plain English. Llama writes the SQL, MySQL runs it.")

if "history" not in st.session_state:
    st.session_state["history"] = []

# Show earlier turns
for turn in st.session_state["history"]:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        render_result(turn["result"])

# New question: typed, or clicked from the sidebar
typed = st.chat_input("Ask about your data, e.g. Which brand has the most stock?")
question = typed or st.session_state.pop("pending_question", None)

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = answer_question(question)
        render_result(result)
    st.session_state["history"].append({"question": question, "result": result})
