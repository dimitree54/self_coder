import os
from typing import List
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from promts import PREFIX


def load_model(model_name: str, temperature: int) -> ChatOpenAI:
    """
    Load OpenAI GPT model.

    Args:
        model_name: String specifying the model to be used.
        temperature: Integer specifying the temperature to be used.

    Returns:
        An instance of ChatOpenAI model.
    """
    return ChatOpenAI(model_name=model_name, temperature=temperature)


def read_file(file_path: str) -> str:
    """
    Read a file and return its content.

    Args:
        file_path: String specifying the path of the file.

    Returns:
        A string containing the content of the file.
    """
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path: str, updated_code: str) -> None:
    """
    Write updated code to a file.

    Args:
        file_path: String specifying the path of the file.
        updated_code: String specifying the updated code.

    Returns:
        None
    """
    with open(file_path, 'w') as file:
        file.write(updated_code)


def create_chat_template() -> ChatPromptTemplate:
    """
    Create a chat template.

    Returns:
        An instance of ChatPromptTemplate.
    """
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(PREFIX)
    ])


def main():
    """
    Main function to update the code.
    """
    file_path = __file__
    task = input("Enter task: ")

    llm = load_model(model_name="gpt-4", temperature=0)
    chat_template = create_chat_template()
    code = read_file(file_path=file_path)

    updated_code = llm(chat_template.format_prompt(task=task, code=code).to_messages()).content
    write_file(file_path=file_path, updated_code=updated_code)


if __name__ == '__main__':
    load_dotenv()
    main()
