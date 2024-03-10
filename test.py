import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient

from code_snippet_gen.main import app, bots, NOT_RELATED_MSG
from code_snippet_gen.utils.structures import ErrorCodes, APIKey, Prompt
from code_snippet_gen.utils.llm import CodeChatBot

load_dotenv()
client = TestClient(app)

session_id = "not_a_session_id"
INVALID_USER_MESSAGE = "Hi!"
VALID_USER_MESSAGE = "Write a python hello world function"


@pytest.mark.order(2)
def test_create_bot_wrong():
    response = client.post("/create_bot/", json={"key": "wrong_key"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == ErrorCodes.INVALID_BOT.code


@pytest.mark.order(1)
def test_check_bot_no_session():
    response = client.get("/check_bot/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == ErrorCodes.NO_SESSION_FOUND.code


@pytest.mark.order(3)
def test_check_bot_not_exist():
    client.cookies.set("session_id", session_id)
    response = client.get("/check_bot/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == ErrorCodes.NO_BOT_EXISTS.code


@pytest.mark.order(4)
def test_check_bot_invalid_bot():
    bots[session_id] = CodeChatBot(openai_api_key="wrong_key")
    client.cookies.set("session_id", session_id)
    response = client.get("/check_bot/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == ErrorCodes.INVALID_BOT.code
    del bots[session_id]


@pytest.mark.order(5)
def test_create_bot():
    global session_id

    response = client.post("/create_bot/", json={"key": os.getenv("OPENAI_API_KEY")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    session_id = data["session_id"]


@pytest.mark.order(6)
def test_check_bot():
    client.cookies.set("session_id", session_id)
    response = client.get("/check_bot/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.order(7)
def test_receive_prompt_wrong():
    client.cookies.set("session_id", session_id)
    response = client.post("/prompt/", json={"user_input": INVALID_USER_MESSAGE})
    assert response.status_code == 200
    data = response.json()
    assert "successful" in data
    assert data["successful"]
    assert "msg" in data
    assert data["msg"] == NOT_RELATED_MSG


@pytest.mark.order(8)
def test_get_history():
    client.cookies.set("session_id", session_id)
    response = client.get("/history/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.order(9)
def test_receive_prompt():
    client.cookies.set("session_id", session_id)
    response = client.post("/prompt/", json={"user_input": VALID_USER_MESSAGE})
    assert response.status_code == 200
    data = response.json()
    assert "successful" in data
    assert data["successful"]
    assert "msg" in data
    assert data["msg"] != NOT_RELATED_MSG


@pytest.mark.order(10)
def test_get_history():
    client.cookies.set("session_id", session_id)
    response = client.get("/history/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


@pytest.mark.order(11)
def test_chat_messages():
    client.cookies.set("session_id", session_id)
    response = client.get("/chat_messages/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    expected_elems = INVALID_USER_MESSAGE, VALID_USER_MESSAGE, NOT_RELATED_MSG
    assert all([elem in data for elem in expected_elems])
