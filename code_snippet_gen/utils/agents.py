import os
import logging

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class CodeText(BaseModel):
    """
    Call this to find out if a message includes a code snippet or not.
    Given a message it determines if there is a code snippet in it.
    If there is no code in the message, it returns (False, "").
    If there is code in the message, it returns (True, code_text) where code_text is
    only the code related text from the message. It should not include any text
    (e.g. explanation) that is not code itself.
    It is probable that the whole message is a code snippet.
    """

    message: str = Field(description="message to parse and search for code inside it.")
    has_code: bool = Field(
        description="True if the given message includes code, False otherwise."
    )
    code_text: str = Field(
        description="The code snippet included in the message, otherwise empty string.",
    )


class CodeExtractor:
    def __init__(self, openai_api_key: str):
        llm = ChatOpenAI(
            model="gpt-3.5-turbo-1106", openai_api_key=openai_api_key, temperature=0
        )
        code_text_func = convert_to_openai_function(CodeText)
        llm_with_tools = llm.bind_tools([code_text_func])
        self.chain = llm_with_tools | JsonOutputToolsParser()

    def __call__(self, message: str) -> tuple[bool, None | str]:
        response_list = self.chain.invoke(message)
        if not isinstance(response_list, list) or len(response_list) != 1:
            return False, None

        response = response_list[0]
        if not isinstance(response, dict) or response["type"] != CodeText.__name__:
            return False, None
        response_args = response.get("args", dict())
        has_code = response_args.get("has_code", False)
        code_text = response_args.get("code_text", message)
        return has_code, code_text
