from typing import List, Optional
import os
import sys
import uuid
import logging
import subprocess
from subprocess import CalledProcessError, run, PIPE

import uvicorn
from fastapi import FastAPI, Cookie, Response, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from code_snippet_gen.utils.llm import CodeChatBot, NOT_RELATED_KEY
from code_snippet_gen.utils.structures import ErrorCodes, APIKey, Prompt, Snippet

PORT = 8000
NOT_RELATED_MSG = "This message is not related to programming."

app = FastAPI()

current_file_path = os.path.abspath(os.path.dirname(__file__))
static_files_path = os.path.join(current_file_path, "static")
app.mount("/static", StaticFiles(directory=static_files_path), name="static")

bots: dict[str, CodeChatBot] = dict()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_session_id():
    return str(uuid.uuid4())


def change_not_related(msg):
    return msg if msg != NOT_RELATED_KEY else NOT_RELATED_MSG


@app.get("/")
async def read_index():
    return FileResponse("static/chat.html")


@app.post("/create_bot/", response_model=dict[str, str])
async def create_bot(
    response: Response, api_key: APIKey, session_id: str = Cookie(None)
):
    if not session_id:
        session_id = generate_session_id()
        response.set_cookie(key="session_id", value=session_id)
    logger.debug(f"{session_id=}")
    logger.debug(f"{api_key.key=}")
    bot = bots.get(session_id) or CodeChatBot(api_key.key)

    if not bot.is_valid():
        error = ErrorCodes.INVALID_BOT
        return {"status": "error", "code": error.code, "msg": error.message}

    bots[session_id] = bot
    return {"status": "ok", "session_id": session_id}


@app.get("/check_bot/")
async def check_bot(session_id: str = Cookie(None)):
    if session_id is None:
        error = ErrorCodes.NO_SESSION_FOUND
        return {"status": "error", "code": error.code, "msg": error.message}
    bot: Optional[CodeChatBot] = bots.get(session_id)
    if bot is None:
        error = ErrorCodes.NO_BOT_EXISTS
        return {"status": "error", "code": error.code, "msg": error.message}

    if not bot.is_valid():
        error = ErrorCodes.INVALID_BOT
        return {"status": "error", "code": error.code, "msg": error.message}
    return {"status": "ok"}


@app.get("/chat_messages/", response_model=List[str])
async def get_chat_messages(session_id: str = Cookie(None)):
    bot = bots.get(session_id)
    if bot is None:
        return RedirectResponse(url="/create_bot/")
    chat_messages = [change_not_related(msg) for msg in bot.processed_history]
    logger.debug(f"{chat_messages=}")
    return chat_messages


@app.post("/prompt/")
async def receive_prompt(prompt: Prompt, session_id: str = Cookie(None)):
    bot = bots.get(session_id)
    if bot is None:
        return RedirectResponse(url="/create_bot/")
    msg = bot(prompt.user_input)
    sucessful = False if msg is None else True
    msg = change_not_related(msg)
    response = {"successful": sucessful, "msg": msg}
    logger.debug(f"{response=}")
    return response


@app.get("/history/", response_model=List[str])
async def get_history(session_id: str = Cookie(None)):
    bot = bots.get(session_id)
    if bot is None:
        return RedirectResponse(url="/create_bot/")
    return bot.snippets_history


@app.post("/delete-snippet/")
async def delete_snippet(snippet: Snippet, session_id: str = Cookie(None)):
    logger.debug(f"delete_snippet({snippet.index}, {session_id})")
    bot = bots.get(session_id)
    if bot is None:
        return RedirectResponse(url="/create_bot/")
    res = bot.delete_snippet(snippet)
    if res:
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Snippet not found")


@app.post("/execute/")
async def execute(snippet: Snippet, session_id: str = Cookie(None)):
    try:
        bot = bots.get(session_id)
        if bot is None:
            return RedirectResponse(url="/create_bot/")
        logger.debug(f"{snippet=}")
        bot.update_snippet(snippet)
        process = run(
            [sys.executable, "-c", snippet.code], text=True, stdout=PIPE, stderr=PIPE
        )
        logger.debug(f"{process.stdout=}")
        process.check_returncode()
        return {"output": process.stdout}

    except CalledProcessError as e:
        output = f"An error occurred:\n{e.stderr}"
        return {"output": output}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/favicon.ico")
async def favicon():
    return Response(content="", status_code=204)


if __name__ == "__main__":
    # log_config = uvicorn.config.LOGGING_CONFIG
    # log_config["formatters"]["access"][
    #     "fmt"
    # ] = "%(asctime)s - %(levelname)s - %(message)s"
    # log_config["formatters"]["default"][
    #     "fmt"
    # ] = "%(asctime)s - %(levelname)s - %(message)s"
    # uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="debug", log_config=log_config)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="debug")
