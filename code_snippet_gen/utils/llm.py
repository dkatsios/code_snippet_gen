from typing import Optional
import os
import logging

from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.llms import LlamaCpp

# from code_snippet_gen.utils.agents import CodeExtractor
from code_snippet_gen.utils.structures import Snippet

logger = logging.getLogger(__name__)

PAR_DIR = os.path.abspath(os.path.dirname(__file__))

NOT_RELATED_KEY = "NOT_RELATED"
EXPLANATION_KEY = "EXPLANATION"
CODE_KEY = "CODE"


class CodeChatBot:
    def __init__(
        self,
        openai_api_key: None | str,
        remote_model_name: None | str = "gpt-3.5-turbo-1106",
    ):
        # openai_api_key = None
        logger.info(f"instantiating CodeChatBot with key: {openai_api_key}")
        self.is_local = not openai_api_key
        self.chat = self._get_chat(openai_api_key, remote_model_name)
        self._handle_system_prompt()

        self.chat_history = ChatMessageHistory()
        self.processed_history = []
        self.snippets_history = []

    def _get_chat(self, openai_api_key: None | str, remote_model_name: None | str):
        if self.is_local:
            return self._get_local_llm()
        return self._get_remote_llm(openai_api_key, remote_model_name)

    def _get_local_llm(self) -> LlamaCpp:
        model_path = os.path.join(PAR_DIR, "models", "llama-2-7b-chat.Q5_K_M.gguf")
        return LlamaCpp(
            model_path=model_path,
            n_gpu_layers=-1,
            n_batch=512,
            temperature=0,
            # top_k=1,
            verbose=False,
        )

    def _get_remote_llm(
        self, openai_api_key: str, remote_model_name: None | str
    ) -> ChatOpenAI:
        return ChatOpenAI(
            model=remote_model_name, openai_api_key=openai_api_key, temperature=0
        )

    def _handle_system_prompt(self):
        system_prompt_path = os.path.join(PAR_DIR, "system_prompt.txt")
        with open(system_prompt_path, encoding="utf-8") as f:
            system_prompt = f.read()
        self.system_prompt = system_prompt.format(
            not_related_key=NOT_RELATED_KEY,
            explanation_key=EXPLANATION_KEY,
            code_key=CODE_KEY,
        )
        if not self.is_local:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )
            self.chain = prompt | self.chat

    def is_valid(self):
        try:
            self.chat.invoke("This is a test message. Do not respond.")
        except Exception as e:
            logger.debug(f"is_valid() exception: {e}")
            return False
        return True

    def __call__(self, msg: str) -> Optional[str]:
        logger.info("Bot call:")
        logger.info(f"User: {msg}")
        self.chat_history.add_user_message(msg)
        self.processed_history.append(msg)
        if self.is_local:
            response = self._call_local()
        else:
            response = self._call_remote()
        if response is None:
            return response
        logger.info(f"Bot: {response}")
        logger.info(f"Current history:\n{self.chat_history.messages}")
        response_text = self._postprocess_response(response)
        logger.info(f"{response_text=}")
        return response_text

    def _call_local(self) -> None | str:
        prompt = self._get_local_prompt()
        response = self.chat.invoke(prompt)
        self.chat_history.add_ai_message(response)
        return response

    def _call_remote(self) -> None | str:
        try:
            response = self.chain.invoke({"messages": self.chat_history.messages})
        except:
            return None
        self.chat_history.add_ai_message(response)
        return response.content

    def _postprocess_response(self, content: str) -> tuple[bool, None | str]:
        logger.info(f"{content=}")
        content = content.strip()
        if content == NOT_RELATED_KEY:
            self.processed_history.append(content)
            return NOT_RELATED_KEY
        if content.startswith(EXPLANATION_KEY):
            content = content[len(EXPLANATION_KEY) :].strip(" \n\t:")
            self.processed_history.append(content)
            return content
        if content.startswith(CODE_KEY):
            content = content[len(CODE_KEY) :].strip(" \n\t:")
            content = "\n".join(
                [line for line in content.split("\n") if not line.startswith("```")]
            )
            self.processed_history.append(content)
            self.snippets_history.append(content)
            return content
        return None

    def delete_snippet(self, snippet: Snippet):
        logger.info(f"{snippet=}")
        if isinstance(snippet.index, int) and 0 <= snippet.index < len(
            self.snippets_history
        ):
            del self.snippets_history[snippet.index]
            return True
        return False

    def update_snippet(self, snippet: Snippet):
        self.snippets_history[snippet.index] = snippet.code

    def _get_local_prompt(self):
        prompt = f"<<SYS>>{self.system_prompt}\n<</SYS>>\n<<HISTORY>>"
        for msg in self.chat_history.dict()["messages"]:
            sender = msg["type"].capitalize()
            content = msg["content"]
            prompt += f"\n{sender}: {content}"
        prompt += "\n<</HISTORY>>\nAI: "
        return prompt
