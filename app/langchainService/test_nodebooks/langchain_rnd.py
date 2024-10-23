import json
import logging
import time
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.langchainService.test_nodebooks.ex_prompts import (
    CHOICE_PROMPT,
    SYSTEM_PROMPT,
    FIRST_STEP_PROMPT,
    TOOL_CALLING_PROMPT
)
from app.langchainService.langchain_util import(
    GenerateQuery,
    ExecutreQuery
)
from app.utils.settings import GROQ_API_KEY

logging.basicConfig(level="INFO")
logger = logging.getLogger("langchain_service")
# api_key = <key>
# base_url = "https://api.ngc.nvidia.com/v2/"
# model = "ai-llama3-8b"
# chat_llm = ChatNVIDIA(
#     model=model,
#     temperature=0.5,
#     beam_width=5,
#     tokens=1024,
#     top_p=1,
#     max_tokens=1024,
#     streaming=True,
#     api_key=api_key
# )

# UNCOMMENT to use for prod. currenly using nvida api for developement
# chat_llm = TritonTensorRTLLM(
#     server_url="http://localhost:8000",
#     model_name="ensemble",
#     temperature=0.2,
#     beam_width=2,
#     tokens=500,
# )
chat_llm = ChatGroq(
    temperature=0,
    api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192"
)

def choice(options: list, input:str, role:str = "assistant"):
    zsc_prompt = ChatPromptTemplate.from_messages(
        [
            # *chat_history,
            ("system", CHOICE_PROMPT.format(options=options)),
            (role, "[Options : {options}] {input} = ")
        ]
    )

    zsc_chain = zsc_prompt | chat_llm | StrOutputParser()
    selected_option = zsc_chain.invoke({"input" : input, "options" : options})
    return selected_option

def respond(user_question: str):
    form = json.dumps({"questions": []})
    prompt = ChatPromptTemplate.from_messages(
        [ 
            ("system", SYSTEM_PROMPT.format(user_question="")),
            ("user", user_question)
        ]
    )
    conversation_chain = prompt | chat_llm | StrOutputParser()
    response = conversation_chain.invoke({"user_question": user_question, "form": form})
    logger.info(f"\n{response}\n")
    return response

def conversation(user_question: str):
    logger.info(f"User Question: {user_question}")
    decide = choice(["respond", "data"], SYSTEM_PROMPT.format(user_question=user_question), role="user")
    logger.info(f"\nIntent Recognition: {decide}\n")
    form = json.dumps({"questions": []})
    if "data" in decide:
        # TODO
        return 0 
    else:
        response = respond(user_question=user_question)
    return response

def generate_query(user: str):
    # TODO: call sql llm to generate a query
    queries = []
    query = """Select
    *
    FROM
    Table
    Limit 10
    """
    queries.append(query)
    return {"response": queries}


def execute_query(queries: str):
    # TODO: execute the queries on Postgres db
    return {"response": "No data for user question in db"}
    
def agent_test(user_question: str):
    generate_sql_query = Tool(
        name="generate_query",
        func=generate_query,
        description="Based on question, this asks an LLM trained to generate sql queries on Users Database",
        args_schema=GenerateQuery
    )
    execute_sql_query = Tool(
        name="execute_query",
        func=execute_query,
        description="Executes the queries generated in previous step to get the data required to answer users quesion.",
        args_schema=ExecutreQuery
    )
    tools_list = [generate_sql_query, execute_sql_query]
    print(tools_list)
    tool_names = ["generate_query", "execute_query"]
    # prompt = SYSTEM_PROMPT.format(user_question="") + "\n" + TOOL_CALLING_PROMPT.format(
    #     tools=tools_list,
    #     tool_names=tool_names,
    #     input=user_question,
    #     agent_scratchpad = []
    # )
    prompt = hub.pull("hwchase17/structured-chat-agent")
    agent = create_structured_chat_agent(
        llm=chat_llm,
        tools=tools_list,
        prompt=prompt,
    )
    logger.info("inititalizing retrival process")
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_list,
        verbose=True,
        handle_parsing_errors=True
    )
    response = agent_executor({"input": user_question})
    logger.info(response)
    return response
    
def ask_lang(query: str):
    start_time = time.time()
    # conversation(user_question="On which channel flood was discussed the most")
    agent_test(user_question=query)
    end_time = time.time()
    time_taken = end_time - start_time
    logger.info(f"Assistant took {time_taken}s to respond")
    