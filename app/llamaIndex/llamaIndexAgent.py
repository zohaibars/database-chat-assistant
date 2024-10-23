import time
import json
import logging
from phoenix.trace import SpanEvaluations
from phoenix.session.evaluation import (
    get_qa_with_reference,
    get_retrieved_documents
)
from llama_index.core.llms import ChatResponse
from llama_index.core import (
    PromptTemplate,
    Settings,
    SQLDatabase,
    VectorStoreIndex,
    StorageContext,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.groq import Groq
from llama_index.llms.nvidia_triton import NvidiaTriton
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    InputComponent,
    FnComponent
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    SimpleObjectNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from sqlalchemy import MetaData
from app.llamaIndex.llamaIndex_utils import (
    REDMINE_TABLES,
    EXAMPLES, 
    TEXT_TO_SQL_PROMPT,
    RESPONSE_SYNTHESIS_PROMPT,
    STRATEGY_PROMPT
)
from app.utils.connections import (
    chromadb_connection,
    mysql_connection,
    llms_clients_index
)
from app.utils.settings import GROQ_API_KEY

logging.basicConfig(level="INFO")
logger = logging.getLogger("Redmine-Assitant")
try:
    engine = mysql_connection()
    metadata_obj = MetaData()
    sql_database = SQLDatabase(engine)
    tables = [*REDMINE_TABLES.keys()]
    metadata_obj.reflect(bind=engine, only=tables)
except:
    logger.info("Invalid MySQL db")

def llms_clients():
    logger.info("Initializing LLM and Embedings")
    api_key=GROQ_API_KEY
    chat_llm = Groq(model="llama3-8b-8192",
    api_key=api_key,
    temperature=0.3
    )
    #triton_url = "localhost:8001"
    #model_name = "ensemble"
    #chat_llm = NvidiaTriton(server_url=triton_url, model_name=model_name)
    embediing_model = HuggingFaceEmbedding(model_name='intfloat/e5-base-v2')
    Settings.embed_model=embediing_model
    return chat_llm, embediing_model

def strategy_pipeline(query: str):
    chat_llm, Settings.embed_model = llms_clients_index()
    db_retriever = set_up_database_retriever(
        sql_database=sql_database,
        metadata_obj=metadata_obj,
        top_k=5
    )
    strategy_template = PromptTemplate(STRATEGY_PROMPT)
    table_parser_component = FnComponent(fn=get_context_string)
    ex_retriever = FnComponent(fn=retrieve_examples)
    strategy_prompt = strategy_template.partial_format(
        dialect=engine.dialect.name
    )

    qp = QP(
        modules={
            "input": InputComponent(),
            "table_retriever": db_retriever,
            "examples": ex_retriever,
            "table_output_parser": table_parser_component,
            "strategy_prompt": strategy_prompt,
            "strategy_llm": chat_llm,
        }
    )
    qp.add_chain(["input", "table_retriever", "table_output_parser"])
    qp.add_chain(["input", "examples"])
    qp.add_link("input", "strategy_prompt", dest_key="query_str")
    qp.add_link("table_output_parser", "strategy_prompt", dest_key="schema")
    qp.add_link("examples", "strategy_prompt", dest_key="examples")
    qp.add_chain(["strategy_prompt", "strategy_llm"])
    
    strategy = qp.run(query=query)
    return strategy

def query_pipeline(query: str):
    start_time = time.time()
    logger.info("Setting up pipline components")
    chat_llm, Settings.embed_model = llms_clients_index()
    db_retriever = set_up_database_retriever(
        sql_database=sql_database,
        metadata_obj=metadata_obj,
        top_k=5
    )
    sql_template = PromptTemplate(TEXT_TO_SQL_PROMPT)
    table_parser_component = FnComponent(fn=get_context_string)
    ex_retriever = FnComponent(fn=retrieve_examples)
    extract_sql_query = FnComponent(fn=sql_parser)
    sql_retriever = SQLRetriever(sql_database)
    rows_parser = FnComponent(fn=parse_rows)
    response_prompt = PromptTemplate(RESPONSE_SYNTHESIS_PROMPT)
    response_prompt = response_prompt.partial_format(
        query_str=query,
        
    )
    output_parser = FnComponent(fn=response_parser)
    time_taken = time.time() - start_time
    logger.info(f"time taken to set up components:{time_taken}s")
    
    logger.info("Running User query")
    start_time = time.time()

    text2sql_prompt = sql_template.partial_format(
    dialect=engine.dialect.name
    )
    qp = QP(
        modules={
            "input": InputComponent(),
            "table_retriever": db_retriever,
            "examples": ex_retriever,
            "table_output_parser": table_parser_component,
            "text2sql_prompt": text2sql_prompt,
            "text2sql_llm": chat_llm,
            "extract_sql_query": extract_sql_query,
            "sql_retriever": sql_retriever,
            "rows_parser": rows_parser,
            "response_prompt": response_prompt,
            "final_response_llm": chat_llm,
            "response_parser": output_parser
        },
        verbose=True,
    )
    qp.add_chain(["input", "table_retriever", "table_output_parser"])
    qp.add_chain(["input", "examples"])
    qp.add_link("input", "text2sql_prompt", dest_key="query_str")
    qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
    qp.add_link("examples", "text2sql_prompt", dest_key="examples")
    qp.add_chain(["text2sql_prompt", "text2sql_llm", "extract_sql_query", "sql_retriever", "rows_parser"])
    qp.add_link("rows_parser", "response_prompt", dest_key="context_str")
    qp.add_link("extract_sql_query", "response_prompt", dest_key="sql_query")
    qp.add_chain(["response_prompt", "final_response_llm"])
    qp.add_chain(["final_response_llm", "response_parser"])
    try:
        response = qp.run(query=query)
    except Exception as ex:
        response = f"Could not retrieve data from db. Be more specific"
        logger.info(f"Error: {ex}")
    time_taken = time.time() - start_time
    logger.info(f"Time taken to respond:{time_taken}s")
    logger.info(type(response))
    return response

def set_up_database_retriever(sql_database: SQLDatabase, metadata_obj: MetaData, top_k: int):
    # creating a vector store
    chroma_collection = chromadb_connection(collection="sql_tables")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # Creating index for each table in database
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = []
    for table_name in metadata_obj.tables.keys():
        table = SQLTableSchema(table_name=table_name)
        table.context_str = REDMINE_TABLES[table_name]["description"]
        table_schema_objs.append(table)
        
    db_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
        storage_context
    )
    db_retriever = db_index.as_retriever(similarity_top_k=top_k)
    return db_retriever

def get_context_string(table_data: List[SQLTableSchema]):
    """
    The get_context_string function takes a list of SQLTableSchema objects and returns a string.
    The string is the table context for the tables in the list.
    
    
    :param table_data: List[SQLTableSchema]: Get the table name
    :return: A string that contains the table and column description for each of the tables in the query
    """
    context_strs = []
    for table_schema_obj in table_data:
        # table_info = REDMINE_TABLES[table_schema_obj.table_name]
        table_info = sql_database.get_single_table_info(
            table_schema_obj.table_name
        )
        additional_info = REDMINE_TABLES[table_schema_obj.table_name]
        table_desc = additional_info["description"]
        important_columns = json.dumps(additional_info["important_columns"], indent=2)
        schema = json.dumps(table_info, indent=4)
        context_str = f"{schema}\n\n"  
        context_str += f"Table description for table '{table_schema_obj.table_name}':\n{table_desc}\n\n"
        context_str += f"Some important columns and descriptions for table '{table_schema_obj.table_name}':\n{important_columns}\n"
        context_strs.append(context_str)
    return "\n\n".join(context_strs)

def retrieve_examples(query: str, top_k: int = 3):
    chroma_collection = chromadb_connection(collection="sql_examples")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    node_mappings = SimpleObjectNodeMapping.from_objects(EXAMPLES)
    obj_idx = ObjectIndex.from_objects(
        EXAMPLES,
        node_mappings,
        VectorStoreIndex,
        storage_context
    )
    retriever = obj_idx.as_retriever(similarity_top_k=top_k)
    relavent_examples = retriever.retrieve(query)
    template = """Example Question: {question}\n
SQL Query:
    {sql_query}"""
    relavent_examples = [
        template.format(
            question=example["query"],
            sql_query=example["passage"]
        )
        for example in relavent_examples
    ]
    
    str_examples = "\n\n".join(relavent_examples)
    return str_examples

def sql_parser(response: ChatResponse):
    """Parse response to SQL."""
    response = response.message.content
    check = "select no;"
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:") :]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    if response.lower().strip().strip("```").strip() == check:
        return "SELECT * FROM rx_statistics_charts;"
    return response.strip().strip("```").strip()

def parse_rows(node):
    rows = node[0].node.text
    return rows

def response_parser(response: ChatResponse):
    response = response.message.content
    return response

    
def ask(query: str):
    response = query_pipeline(
        query=query
    )
    # response = strategy_pipeline(
    #     chat_llm=chat_llm,
    #     query=query        
    # )
    # logger.info(f"Check traces here:{px.active_session().url}")
    return response

