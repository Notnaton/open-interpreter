from pydantic import BaseModel
from typing import List

from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.litellm import LiteLLM

class Chat(BaseModel):
    title: str
    content: str

class Code(BaseModel):
    language: str
    content: str

class Response(BaseModel):
    plan: Chat
    code: Code

def run_structured_output_llm(oillm, params):

    if oillm.interpreter.computer.terminal.languages != []:
        try:
            # Add the system message
            params["messages"][0][
                "content"
            ] += "\nTo execute code on the user's machine, write a markdown code block. Specify the language after the ```. You will receive the output. Use any programming language."
        except:
            print('params["messages"][0]', params["messages"][0])
            raise

    llm = LiteLLM(**oillm)
    
    test = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_cls=Response,
        prompt_template_str="Fill in the fields using the user prompt as context"
    )

    output = test()

    return output

