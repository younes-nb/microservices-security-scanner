import os
from langchain_core.tools import tool

@tool
def list_files(path: str) -> str:
    """
    Use this to list the files and directories in a given path.
    Input should be a valid file path.
    """
    cleaned_path = path.strip("'\"\n ")
    print(f"TOOL: Listing files in cleaned path: '{cleaned_path}'")
    try:
        entries = os.listdir(cleaned_path)
        return "\n".join(entries)
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def read_file(file_path: str) -> str:
    """
    Use this to read the full content of a specific file.
    The input must be a valid file path.
    """
    cleaned_path = file_path.strip("'\"\n ")
    print(f"TOOL: Reading file: '{cleaned_path}'")
    try:
        with open(cleaned_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def read_multiple_files(file_paths: list[str]) -> str:
    """
    Use this to read the full content of a list of specific files.
    The input must be a list of valid file paths.
    """
    all_content = ""
    for file_path in file_paths:
        cleaned_path = file_path.strip("'\"\n ")
        print(f"TOOL: Reading file: '{cleaned_path}'")
        try:
            with open(cleaned_path, 'r', encoding='utf-8') as f:
                all_content += f"--- CONTENT OF {cleaned_path} ---\n"
                all_content += f.read()
                all_content += "\n\n"
        except Exception as e:
            all_content += f"--- ERROR READING {cleaned_path}: {e} ---\n\n"
    return all_content