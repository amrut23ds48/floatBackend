import psycopg2
from psycopg2.extras import RealDictCursor
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URI")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_sql(sql: str) -> str:
    sql = sql.strip()
    if sql.startswith("```") and sql.endswith("```"):
        sql = sql[3:-3].strip()
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()
    return sql


def run_query(sql: str):
    """Run a SELECT query and return rows."""
    sql = clean_sql(sql)
    if not sql.lower().startswith("select"):
        return {"error": "Only SELECT queries are allowed."}
    # Create a new connection for each query to avoid closed connection errors
    with psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

def ask_llm(question: str):
    """Ask LLM to generate SQL, execute it, and summarize results."""
    
    sql_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert SQL assistant. only Generate a SELECT query for the argo_observations table and nothing else."},
            {"role": "user", "content": f"Write a SQL query to answer: {question}"}
        ]
    )
    sql_query = sql_response.choices[0].message.content.strip()
    print("Generated SQL:", sql_query)

    rows = run_query(sql_query)

    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that explains database results."},
            {"role": "user", "content": f"Question: {question}\nResults: {rows}\nSummarize the results in plain English."}
        ]
    )
    return summary_response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    answer = ask_llm("What is highest depth recorded?")
    print("Answer:", answer)