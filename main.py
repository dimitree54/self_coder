from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

from code_improver import improve_code
from code_reviewer import review_code, get_diff
from utils import IssueInfo


def update_code(code: str, issue_info: IssueInfo, max_reviews: int = 3) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    code_to_improve = code
    review = ""
    for i in range(max_reviews):
        improved_code = improve_code(llm=llm, code_to_improve=code_to_improve, issue_info=issue_info, review=review)
        code_diff = get_diff(code_before=code_to_improve, code_after=improved_code)
        review = review_code(llm=llm, code_diff=code_diff, issue_info=issue_info)
        if review is None:
            return improved_code
        else:
            code_to_improve = improved_code
    raise Exception("Max reviews exceeded")


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path: str, updated_code: str) -> None:
    with open(file_path, 'w') as file:
        file.write(updated_code)


def main():
    file_path = __file__
    task = input("Enter task: ")
    code = read_file(file_path=file_path)
    guidelines = read_file(file_path=str(Path(__file__).parent / "GUIDELINES.txt"))
    requirements = read_file(file_path=str(Path(__file__).parent / "requirements.txt"))
    updated_code = update_code(code, IssueInfo(task=task, guidelines=guidelines, requirements=requirements))
    write_file(file_path=file_path, updated_code=updated_code)


if __name__ == '__main__':
    load_dotenv()
    main()
