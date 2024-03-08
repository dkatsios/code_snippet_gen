import os
import requests
from dotenv import load_dotenv

load_dotenv()


# The URL of the FastAPI backend
BASE_URL = "http://0.0.0.0:8000"


def set_wrong_key():
    api_key = "test"
    response = requests.post(f"{BASE_URL}/set_key/", json={"key": api_key})
    if response.status_code == 200:
        print("API key was set successful:", response.json())
    else:
        print("Failed to set api key")


def set_key():
    api_key = os.getenv("OPENAI_API_KEY")
    response = requests.post(f"{BASE_URL}/set_key/", json={"key": api_key})
    if response.status_code == 200:
        print("API key was set successful:", response.json())
    else:
        print("Failed to set api key")


def test_bad_prompt():
    prompt_text = "Hello, what is your name."
    response = requests.get(f"{BASE_URL}/prompt/", json={"user_input": prompt_text})
    if response.status_code == 200:
        print("Prompt submission successful:", response.json())
    else:
        print("Failed to submit prompt", response.content)


def test_good_prompt():
    prompt_text = "Write a code snippet to print 'hello' in python language"
    response = requests.get(f"{BASE_URL}/prompt/", json={"user_input": prompt_text})
    if response.status_code == 200:
        print("Prompt submission successful:", response.json())
    else:
        print("Failed to submit prompt", response.content)


def test_history():
    response = requests.get(f"{BASE_URL}/history/")
    if response.status_code == 200:
        print("History retrieval successful:", response.json())
    else:
        print("Failed to retrieve history")


if __name__ == "__main__":
    set_wrong_key()
    test_good_prompt()
    set_key()
    test_bad_prompt()
    test_good_prompt()
    test_history()
