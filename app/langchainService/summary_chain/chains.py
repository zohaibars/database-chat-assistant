from app.langchainService.summary_chain.summary_prompt import (
    CORRECTION_PROMPT,
    TOPIC_SUMMARIZATION_PROMPT,
    RUNNING_SUMMARY_PROMPT
)
from langchain_core.output_parsers.string import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import PromptTemplate

# Topcis chain
def get_topic_chain(llm):
    topic_prompt = PromptTemplate.from_template(TOPIC_SUMMARIZATION_PROMPT)
    topic_summarization_chain = topic_prompt | llm | StrOutputParser()
    return topic_summarization_chain
# Running summary  chain
def get_summary_chain(llm):
    running_summary_prompt = PromptTemplate.from_template(RUNNING_SUMMARY_PROMPT)
    running_summary_chain = running_summary_prompt | llm | StrOutputParser()
    return running_summary_chain