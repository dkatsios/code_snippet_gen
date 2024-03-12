import os
from langchain.memory import ChatMessageHistory
from langchain_community.llms import LlamaCpp


model_path = os.path.join(
    os.getcwd(),
    "utils",
    "models",
    # "rift-coder-v0-7b-q4_0.gguf",
    # "orca-mini-3b-gguf2-q4_0.gguf",
    "llama-2-7b-chat.Q5_K_M.gguf",
)

llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=-1,
    n_batch=512,
    temperature=0,
    # top_k=1,
    verbose=False,
)


NOT_RELATED_KEY = "NOT_RELATED"
EXPLANATION_KEY = "EXPLANATION"
CODE_KEY = "CODE"

system_prompt_path = os.path.join(os.getcwd(), "utils", "system_prompt.txt")
with open(system_prompt_path, encoding="utf-8") as f:
    system_prompt = f.read()

system_prompt = system_prompt.format(
    not_related_key=NOT_RELATED_KEY,
    explanation_key=EXPLANATION_KEY,
    code_key=CODE_KEY,
)
chat_history = ChatMessageHistory()


def get_prompt(system_prompt, chat_history):
    prompt = f"<<SYS>>{system_prompt}\n<</SYS>>\n<<HISTORY>>"
    for msg in chat_history.dict()["messages"]:
        sender = msg["type"].capitalize()
        content = msg["content"]
        prompt += f"\n{sender}: {content}"
    prompt += "\n<</HISTORY>>\nAI: "
    return prompt


def call(msg, llm, system_prompt, chat_history):
    chat_history.add_user_message(msg)
    prompt = get_prompt(system_prompt, chat_history)
    # print(prompt)
    response = llm.invoke(prompt)
    chat_history.add_ai_message(response)
    return response


response = call("hi there!", llm, system_prompt, chat_history)
print(response)


response = call(
    "write a python function for factorial of a given number",
    llm,
    system_prompt,
    chat_history,
)
print(response)
