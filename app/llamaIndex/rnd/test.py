from llama_index.llms.nvidia_triton import NvidiaTriton
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
triton_url = "localhost:8001"
model_name = "ensemble"
prompt = """System: {System}

{Context}

User: {Question}

Assistant:"""

sys = "You are a help full assistant for every thing"
ctx = ""
user = "Can you write a complete news article, 250 words, about the recent advances in renewable energy? "
qes = prompt.format(
   System=sys,
   Context=ctx,
   Question=user
)
resp = NvidiaTriton(
   server_url=triton_url,
   model_name=model_name,
   tokens=1024,
   temperature=1
).complete(qes)
print(resp)
