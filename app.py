"""Text-to-SQL demo: ask a question in English, get an answer from MySQL."""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase

load_dotenv()

# 1. Connect to MySQL (settings come from .env)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "atliq_tshirts")

db = SQLDatabase.from_uri(
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}",
    sample_rows_in_table_info=3,
)

# 2. Load Ollama
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.2"), temperature=0)

# 3. Ask your question
question = "Rank all brands by their total inventory value from highest to lowest."

# 4. Give database schema + question to the model
prompt = f"""You are a MySQL expert.

Database schema:
{db.get_table_info()}

Question:
{question}

Write only the SQL query, nothing else."""

# 5. The model creates SQL (remove markdown fences if it adds them)
sql = llm.invoke(prompt).content.strip()
sql = sql.replace("```sql", "").replace("```", "").strip()

print("SQL:", sql)

# 6. Run the SQL only if it is a read-only query
if not sql.upper().startswith(("SELECT", "WITH")):
    raise SystemExit("The model did not return a SELECT query, so nothing was run.")

result = db.run(sql)
print("Result:", result)

# 7. Convert the result into a normal answer
answer = llm.invoke(
    f"""Question: {question}

Database result: {result}

Answer in one short sentence using only this result."""
).content

print("Answer:", answer)
