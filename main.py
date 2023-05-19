from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate

from promts import PREFIX

load_dotenv()


def main():
    file_path = __file__

    with open(file_path, 'r') as file:
        code = file.read()

    task = input("Enter task: ")

    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    chat_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(PREFIX)
    ])
    updated_code = llm(chat_template.format_prompt(task=task, code=code).to_messages()).content
    with open(file_path, 'w') as file:
        file.write(updated_code)


if __name__ == '__main__':
    main()
