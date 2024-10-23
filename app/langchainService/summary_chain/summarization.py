import requests
import logging
import time
import tiktoken
from sqlalchemy import text
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import PromptTemplate
from app.utils.connections import postgres_connection, llms_clients_lang
from app.langchainService.summary_chain.summary_utils import (
    urdu_proper_nouns,
    urdu_adjectives,
    TopicsOutputParser
)

from app.langchainService.summary_chain.summary_prompt import (
    CORRECTION_PROMPT
)
from app.langchainService.summary_chain.chains import get_topic_chain, get_summary_chain
from app.utils.settings import TRANSLATION_URL
from typing import List

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)
llm = llms_clients_lang(model="llama3-8b-8192")
TOKEN_LIMIT = 150

def get_recent_STT():
    engine = postgres_connection()
    query = """SELECT
        transcription_urdu
    FROM
        whisper_app_speech_to_text_database
    ORDER BY 
        created_date
    DESC Limit 3;"""
    result = ""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            result_list = [str(value) for row in result.fetchall() for value in row]
            print("PostgresSQL Database results:", result_list)
    except Exception as ex:
        print("Error Couldnt get:\n", ex)
    
    result_list.reverse()
    text_to_process = ".".join(result_list)
    return text_to_process

def get_translation(text: str):
    start_time = time.time()
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    split_index = 0
    for i in range(len(tokens)):
        if i > TOKEN_LIMIT and tokens[i] == encoder.encode(".\n\n")[0]:
            split_index = i
            break
    groups = []    
    if split_index == 0:
        groups = [text]
    else:
        text1 = encoder.decode(tokens[:split_index])
        text2 = encoder.decode(tokens[split_index:])
        text2 = text2.replace(".\n\n", "")
        groups = [text1, text2]
    urdu_translations = []
    for text in groups:
        payload = {'text': text}
        url = TRANSLATION_URL+"/translate"
        try:
            response = requests.post(url=url, json=payload)
            data = response.json()
            urdu_translations.append(data.get("translated_text"))
        except Exception as ex:
            logger.info(f"Error: {ex}")
    end_time = time.time()
    time_taken = end_time - start_time
    
    logger.info(f"Time taken for translation: {time_taken}")
    urdu_translation = ". ".join(urdu_translations)
    return urdu_translation

def get_correction():
    text_to_process = get_recent_STT()
    prompt = PromptTemplate.from_template(CORRECTION_PROMPT)

    correction_chain = prompt | llm | StrOutputParser()
    corrections = correction_chain.invoke(
        {
            "nouns": urdu_proper_nouns,
            "text": text_to_process
        }
    )
    return corrections


def get_summary(docs: List[str], running_summary: List[str], model: str = "llama3-70b-8192"):
    llm = llms_clients_lang(model=model)
    min_current = len(docs)
    min_running = 3 * len(running_summary)
    docs.reverse()
    text_to_process = "\nnext transcript\n".join(docs)
    previous_summaries = "\n".join(running_summary)
    previous_summaries = ""
    topic_summarization_chain = get_topic_chain(llm)
    parser = TopicsOutputParser()
    topic_summaries = topic_summarization_chain.invoke(
        {
            "min_current": min_current,
            "min_running": min_running,
            "urdu": text_to_process,
            "previous_summaries": previous_summaries
        }
    )
    structured_topics = parser.parse(text=topic_summaries)
    running_summary_chain = get_summary_chain(llm)
    currnet_running_summary = running_summary_chain.invoke(
        {
         "current_topics": topic_summaries        }
    )
    urdu_summaries = []
    for topic_summary in structured_topics.topic_summaries:
        urdu = {
            "topic": get_translation(text=topic_summary["topic"]),
            "summary": get_translation(text=topic_summary["summary"])
        }
        urdu_summaries.append(urdu)

    return {
        "topic_summaries":  structured_topics.topic_summaries,
        "urdu_translation": urdu_summaries,
        "running_summary": currnet_running_summary
    }