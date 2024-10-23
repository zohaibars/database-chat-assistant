import logging
import time
import functools
from typing import (
    Annotated,
    Sequence,
    TypedDict,
    Literal,
    Optional,
    Union
)
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import Field
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.langchainService.prompts import (
    ASSISTANT_SYSTEM_PROMPT,
    ASSISTANT_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT,
    SUPERVISOR_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    PLANNER_GENERATION_PROMPT,
    SQL_SYSTEM_PROMPT,
    SQL_GENERATION_PROMPT,
    EVALUATION_SYSTEM_PROMPT,
    EVALUATION_PROMPT, 
    GENERATION_PROMPT
)
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)
from langgraph.graph import END, StateGraph
from app.utils.connections import llms_clients_lang
from app.langchainService.database_retriver import get_table_context, execute_query
from app.langchainService.langchain_util import TaskState, AssistantAgent

logging.basicConfig(level="INFO")
logger = logging.getLogger("Multi-Agent-Db-Assistant")
llm = llms_clients_lang()


def assistant_node(state: TaskState):
    logger.info("Primary assistant")
    prompt = ASSISTANT_PROMPT.format(question=state["task"])
    system = SystemMessage(content=ASSISTANT_SYSTEM_PROMPT)
    user = HumanMessage(content=prompt)
    messages = [system, user]
    response = llm.invoke(messages)
    return {
        "messages": messages,
        "step": response.content
    }

def supervisor_node(state: TaskState):
    logger.info("Supervisor making decision")
    members = ["planner", "sql coder", "evaluator"]
    options = ["FINISH"] + members
    prompt = SUPERVISOR_PROMPT.format(
        options=options,
        status=state["step"] or "plan",
        current=state["revision_number"],
        max=state["max_revisions"],
    )
    system = SystemMessage(
        content=SUPERVISOR_SYSTEM_PROMPT.format(members=members)
    )
    user = HumanMessage(content=prompt)
    
    messages = [system, user]
    response = llm.invoke(messages)
    return {
        "step": response.content
    }

def planner_node(state: TaskState):
    logger.info("Planning phase for the query")
    context = get_table_context(query=state["task"])
    system = SystemMessage(
        content=PLANNER_SYSTEM_PROMPT
    )
    user = HumanMessage(
        content=PLANNER_GENERATION_PROMPT.format(
            table_info=context.get("table_info", ""),
            examples=context.get("examples", ""),
            task=state["task"]
        )
    )
    messages = [system, user]
    response = llm.invoke(messages)
    return {
        "step": "planning completed",
        "table_info": context.get("table_context", ""),
        "examples": context.get("examples", ""),
        "strategy" : response.content,
        "dialect": context.get("dialect", "")
    }

def sql_node(state: TaskState):
    logger.info("Generating the SQL query")
    system = SystemMessage(content = SQL_SYSTEM_PROMPT)
    user = HumanMessage(
        content=SQL_GENERATION_PROMPT.format(
            dialect=state["dialect"],
            table_info=state["table_info"],
            strategy=state["strategy"],
            # examples=state["examples"],
            task=state["task"],
        )
    )
    messages = [system, user]
    response = llm.invoke(messages)
    sql = response.content
    if sql:
        sql_query_start = sql.find("SQLQuery:")
        if sql_query_start != -1:
            sql = sql[sql_query_start:]
            if sql.startswith("SQLQuery:"):
                sql = sql[len("SQLQuery:") :]
        sql_result_start = sql.find("SQLResult:")
        if sql_result_start != -1:
            sql = sql[:sql_result_start]
            sql = sql.replace("```", "").strip()
    sql = sql.replace("SQLQUERY:","").strip()
            
    return {
        "sql_query": sql
    }

def evaluator_node(state: TaskState):
    logger.info("Evaluating the Query and data")
    rows = execute_query(sql_query=state["sql_query"])
    system = SystemMessage(content=EVALUATION_SYSTEM_PROMPT)
    user = HumanMessage(
        content=EVALUATION_PROMPT.format(
            task=state["task"],
            sql=state["sql_query"],
            rows=rows,
        )
    )
    messages = [system, user]
    evaluation = llm.invoke(messages)
    return {
        "evaluation": evaluation.content,
        "revision_number": state.get('revision_number', 0)+1
    }

def generation_node(state: TaskState):
    logger.info("Generating response")
    system = SystemMessage(content=ASSISTANT_SYSTEM_PROMPT)
    user = HumanMessage(
        content=GENERATION_PROMPT.format(
            task=state['task'],
            evaluation=state["evaluation"]
        )
    )
    messages = [system, user]
    response = llm.invoke(messages)
    return {
        "step": "done",
        "final_response": response.content
    }

def condition_check(state: TaskState):
    if state["step"] == "supervisor":
        return "supervisor"
    if state["step"] == "planner":
        return "planner"
    if state["step"] == "sql":
        return "sql coder"
    if state["step"] == "evaluator":
        return "evaluator"
    if state["step"] == "FINISH":
        return "FINISH"

def adaptive_agent(user_question: str, chat_history: list):
    memory = SqliteSaver.from_conn_string(":memory:")
    builder = StateGraph(TaskState)
    logger.info(f"Creating A Cyclic multi agent assistant")
    logger.info("Initializing agents")
    
    builder.add_node("assistant", assistant_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("planner", planner_node)
    builder.add_node("sql coder", sql_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("generate", generation_node)
    builder.add_conditional_edges(
        "assistant",
        condition_check,
        {"FINISH": "generate", "supervisor": "supervisor"}
    )
    builder.add_conditional_edges(
        "supervisor",
        condition_check,
        {
            "FINISH": "generate",
            "planner": "planner",
            "sql coder": "sql coder",
            "evaluator": "evaluator"
        }
    )
    builder.add_edge("planner","supervisor")
    builder.add_edge("sql coder","supervisor")
    builder.add_edge("evaluator","supervisor")
    builder.add_edge("generate", END)
    builder.set_entry_point("assistant")
    graph = builder.compile(checkpointer=memory)
    # creating conversation thread
    thread_config = {"configurable": {"thread_id": "1"}}
    # response = graph.invoke(
    #     {
    #         "task": user_question,
    #         "max_revisions": 1,
    #         "revision_number": 0
    #     }, 
    #     thread_config
    # )
    for event in graph.stream(
             {
            "task": user_question,
            "max_revisions": 2,
            "revision_number": 0
        }, 
        thread_config
    ):
        response = event
        for v in event.values():
            print(v)
    return response
    # return {"question": response['task'], "assistant": response["final_response"]}
   