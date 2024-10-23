from fastapi import FastAPI
from app.llamaIndex.llamaIndexAgent import ask
from app.chat_bot import ask_lang
from app.langchainService.sql_agent_graph import adaptive_agent
from app.langchainService.summary_chain.summarization import get_summary
from app.utils.models import userInput, Docs, summaryResponse
app = FastAPI(
    title="Assistant-api"
)

    
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/ask")
async def ask_llama(request: userInput):
    response = ask(query=request.question)
    return response


@app.post("/ask/lang")
async def ask_lang_agent(request: userInput):
    response = ask_lang(query=request.question)
    return response["output"]


@app.post("/ask/agent")
async def ask_llama(request: userInput):
    response = adaptive_agent(
        user_question=request.question,
        chat_history=request.chat_history
    )
    return response


@app.post("/summarize")
async def summarize(docs: Docs):
    summery = get_summary(model="llama-3.1-8b-instant", docs=docs.input, running_summary= [""])
    return summery


@app.post(
    "/summarize-70b/",
    response_model=summaryResponse
)
async def summarize(docs: Docs):
    summary = get_summary(model="llama3-70b-8192", docs=docs.input, running_summary=docs.running_summaries)
    response = summaryResponse(response=summary)
    return response