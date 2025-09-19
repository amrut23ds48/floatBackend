from fastapi import FastAPI
import os
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
from argo_rag.mcpServer import ask_llm
from argo_rag.src.query_rag import rag_query
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
         "http://localhost:3000",
         "https://floatchat-delta.vercel.app/",
         "http://localhost:5173" 
    ],
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],
)

client = OpenAI(api_key=OPENAI_API_KEY)

messeges = [
    {"role": "system", "content": "you are helpful assistant who gives concise answers"},
    {"role": "user", "content": "give me two mindblowing facts about space"}
]

# response = client.chat.completions.create(
#     model = "gpt-4o-mini",
#     messages = messeges
# )
# reply = response.choices[0].message.content

conn = psycopg2.connect(DATABASE_URI, cursor_factory=RealDictCursor)


@app.get("/")
def root():
    return {"message": "FastAPI + Neon PostgreSQL + psycopg2 is running!"}


@app.get("/chat-query/{query}")
def chat_query(query: str):
    answer = ask_llm(query)
    return {"answer": answer}


