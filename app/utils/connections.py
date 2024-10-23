import chromadb
import psycopg2
from urllib.parse import quote_plus, quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pydantic import PostgresDsn
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.llms.nvidia_triton import NvidiaTriton
from langchain_groq import ChatGroq
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from app.utils.settings import (
    POSTGRES_STT_HOST,
    POSTGRES_STT_DATABASE,
    POSTGRES_STT_USER,
    POSTGRES_STT_PASSWORD,
    POSTGRES_STT_PORT,
    MYSQL_USER,
    MYSQL_PASS,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DB,
    GROQ_API_KEY
)

def chromadb_connection(collection: str):
    db = chromadb.PersistentClient("./chromadb")
    chroma_collection = db.get_or_create_collection(collection)
    return chroma_collection

def mysql_connection():
    pws = quote_plus(MYSQL_PASS)
    connection_string = f"mysql+pymysql://{MYSQL_USER}:%s@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"%pws
    engine = create_engine(url=connection_string) 
    return engine

def sqlite_connection():
    # connection_string = f"mysql://{SQLITE_USER}:{SQLITE_PASS}@{SQLITE_HOST}:{SQLITE_PORT}/{SQLITE_DB}"
    # engine = create_engine(connection_string, future=True)
    engine = create_engine("sqlite:///mydatabase.db", future=True)
    return engine 

def llms_clients_index(temp: float = 0.3):
    
    api_key=GROQ_API_KEY
    chat_llm = Groq(model="llama-3.1-70b-versatile",
    api_key=api_key,
    temperature=temp
    )
    #triton_url = "localhost:8001"
    #model_name = "ensemble"
    #chat_llm = NvidiaTriton(server_url=triton_url, model_name=model_name)
    embediing_model = HuggingFaceEmbedding(model_name='intfloat/e5-base-v2')
    
    return chat_llm, embediing_model

def llms_clients_lang(temp: float = 0.3, model: str = "llama-3.1-70b-versatile"):
    
    api_key=GROQ_API_KEY
    chat_llm = ChatGroq(model=model,
    api_key=api_key,
    temperature=temp
    )
    #triton_url = "localhost:8001"
    #model_name = "ensemble"
    #chat_llm = TritonTensorRTLLM(server_url=triton_url, model_name=model_name)
    return chat_llm

def postgres_connection():
    connection_string = f'postgresql://{POSTGRES_STT_USER}:{POSTGRES_STT_PASSWORD}@{POSTGRES_STT_HOST}:{POSTGRES_STT_PORT}/{POSTGRES_STT_DATABASE}'
    print(connection_string)
    engine = create_engine(connection_string)
    return engine

check = mysql_connection()
check_post = postgres_connection()
