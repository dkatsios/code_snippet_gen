import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

NOT_RELATED = "NOT_RELATED"


class CodeChatBot:
    def __init__(self, openai_api_key: str):
        self.chat_history = ChatMessageHistory()
        self.chat = ChatOpenAI(
            model="gpt-3.5-turbo-1106", openai_api_key=openai_api_key, temperature=0
        )
        prompt = self._get_system_prompt()
        self.chain = prompt | self.chat

    def is_valid(self):
        try:
            self("This is a test message")
        except Exception as ex:
            print(ex)
            return False
        else:
            return True

    def _get_system_prompt(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    You are a code assistant.
                    You only respond to questions related to programming.
                    All your responses have to be valid code snippets.
                    If a user prompt is not related to code or you cannot respond with code
                    you should return the keyword "{NOT_RELATED}" and after that the reason
                    why you could not respond with a code snippet.
                    When possible, try to respond and use the context from previous
                    messages to respond correctly.
                    """,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return prompt

    def __call__(self, msg) -> tuple[bool, Optional[str]]:
        self.chat_history.add_user_message(msg)
        response = self.chain.invoke({"messages": self.chat_history.messages})
        self.chat_history.add_ai_message(response)
        # if response.content.startswith(NOT_RELATED):
        #     return False, None
        return True, response.content

    def get_code_snippets(self):
        code_snippets = [
            msg["content"]
            for msg in self.chat_history.dict()["messages"]
            if msg["type"] == "ai" and msg["content"] != NOT_RELATED
        ]
        return code_snippets
