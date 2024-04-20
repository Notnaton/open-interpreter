from langchain_community.chat_models import ChatLiteLLM

from typing import List

from langchain.output_parsers import YamlOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field


def run_structured_output_llm(llm, params):
    model = ChatLiteLLM(client=llm, **params)

    # Define your desired data structure.
    class Joke(BaseModel):
        setup: str = Field(description="question to set up a joke")
        punchline: str = Field(description="answer to resolve the joke")

    # And a query intented to prompt a language model to populate the data structure.
    joke_query = "Tell me a joke."

    # Set up a parser + inject instructions into the prompt template.
    parser = YamlOutputParser(pydantic_object=Joke)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    chain.invoke({"query": joke_query})






