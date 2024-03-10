from typing import Optional
import os
import logging

from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from code_snippet_gen.utils.agents import CodeExtractor

logger = logging.getLogger(__name__)
NOT_RELATED_KEY = "NOT_RELATED"


class CodeChatBot:
    def __init__(self, openai_api_key: str):
        logger.info(f"instantiating CodeChatBot with key: {openai_api_key}")
        self.chat_history = ChatMessageHistory()
        self.chat = ChatOpenAI(
            model="gpt-3.5-turbo-1106", openai_api_key=openai_api_key, temperature=0
        )
        prompt = self._get_system_prompt()
        self.chain = prompt | self.chat
        self.snippets_history = []
        self.code_extractor = CodeExtractor(openai_api_key)

    def is_valid(self):
        try:
            self.chat.invoke("This is a test message. Do not respond.")
        except Exception as e:
            logger.debug(f"is_valid() exception: {e}")
            return False
        return True

    def _get_system_prompt(self):
        current_file_path = os.path.abspath(os.path.dirname(__file__))
        system_prompt_path = os.path.join(current_file_path, "system_prompt.txt")
        with open(system_prompt_path, encoding="utf-8") as f:
            system_prompt = f.read()
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt.format(not_related_key=NOT_RELATED_KEY),
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return prompt

    def __call__(self, msg: str) -> tuple[bool, Optional[str]]:
        try:
            self.chat_history.add_user_message(msg)
            response = self.chain.invoke({"messages": self.chat_history.messages})
            self.chat_history.add_ai_message(response)
            logger.debug("Bot call:")
            logger.debug(f"User: {msg}")
            logger.debug(f"Bot: {response.content}")
            logger.debug(f"Current history: {self.chat_history.messages}")
            if response.content != NOT_RELATED_KEY:
                self._add_to_snippets_history(response.content)
            return True, response.content
        except:
            return False, None

    def delete_snippet(self, snippet_index: int):
        if isinstance(snippet_index, int) and 0 <= snippet_index < len(
            self.snippets_history
        ):
            del self.snippets_history[snippet_index]
            return True
        return False

    def _add_to_snippets_history(self, message: str):
        logger.debug(f"{message=}")
        has_code, code_text = self.code_extractor(message)
        logger.debug(f"{has_code=}, {code_text=}")
        if has_code:
            self.snippets_history.append(code_text)
