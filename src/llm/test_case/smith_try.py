
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.llm.LLM_options import LLMOptions
import os
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to the user's request only based on the given context."),
    ("user", "Question: {question}\nContext: {context}")
])

cfg={"langchain_key":"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"}
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "LLMCompiler"
os.environ["LANGCHAIN_API_KEY"] = cfg['langchain_key']
model = LLMOptions.getClinetByName("deepseek",temperature=0.5)
output_parser = StrOutputParser()

chain = prompt | model | output_parser

question = "Can you summarize this morning's meetings?"
context = "how to use the langSmith tracer to monitor my application."
print(chain.invoke({"question": question, "context": context}))
