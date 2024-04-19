from pydantic import BaseModel
from typing import List

from llama_index.core.output_parsers import PydanticOutputParser

class Chat(BaseModel):
    title: str
    content: str

class Code(BaseModel):
    language: str
    content: str

class Response(BaseModel):
    plan: Chat
    code: Code

def run_structured_output_llm(llm, params):

    pass

