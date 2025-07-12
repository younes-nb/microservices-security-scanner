import json
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
import re

MODEL = "llama3-groq-tool-use"

def get_explanation(prompt: str) -> str | None:
    try:
        llm = ChatOllama(model=MODEL)
        print("INFO: Calling LLM for explanation...")
        response: AIMessage = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"An error occurred in get_explanation: {e}")
        return None

def select_stereotype_from_explanation(prompt: str, choices: list) -> str | None:
    try:
        llm = ChatOllama(model=MODEL)
        print("INFO: Calling LLM for selection...")
        response: AIMessage = llm.invoke(prompt)
        cleaned_output = _extract_first_match(response.content, choices)
        return cleaned_output
    except Exception as e:
        print(f"An error occurred in select_stereotype_from_explanation: {e}")
        return None

def get_structured_annotations(prompt: str) -> dict | None:
    try:
        llm = ChatOllama(model=MODEL, format="json")
        print("INFO: Calling LLM for structured data extraction (JSON)...")
        response: AIMessage = llm.invoke(prompt)
        return json.loads(response.content)
    except Exception as e:
        print(f"An error occurred in get_structured_annotations: {e}")
        return None

def _extract_first_match(text: str, choices: list[str]) -> str | None:
    pattern = r"\b(" + "|".join(re.escape(choice) for choice in choices) + r")\b"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    if "none" in text.lower():
        return "None"
    return None