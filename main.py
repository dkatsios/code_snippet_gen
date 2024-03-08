from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm import CodeChatBot

PORT = 8000

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

code_chatbot = None


class APIKey(BaseModel):
    key: str


class Prompt(BaseModel):
    user_input: str


@app.get("/")
async def read_index():
    return FileResponse('./static/chat.html')


@app.post("/set_key/", response_model=bool)
async def set_api_key(api_key: APIKey):
    global code_chatbot
    print("running set_api_key()", api_key.key)
    code_chatbot = CodeChatBot(api_key.key)
    is_valid = code_chatbot.is_valid()
    print(f"{is_valid=}")
    if not is_valid:
        code_chatbot = None
        return False
    return True


@app.get("/check_bot/")
async def check_bot():
    if code_chatbot is None or not code_chatbot.is_valid():
        return {"status": "error"}
    return {"status": "ok"}


@app.get("/prompt/")
async def receive_prompt(prompt: Prompt):
    if code_chatbot is None:
        print("code_chatbot is None inside receive_prompt()")
        response = {"successful": False, "msg": None}
    else:
        sucessful, msg = code_chatbot(prompt.user_input)
        response = {"successful": sucessful, "msg": msg}
    print(f"receive_prompt response: {response}")
    return response


# Endpoint to get the history of prompts and responses
@app.get("/history/", response_model=List[str])
async def get_history():
    if code_chatbot is None:
        return []
    return code_chatbot.get_code_snippets()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="debug")
