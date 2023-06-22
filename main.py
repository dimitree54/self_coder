from pathlib import Path

from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from yid_langchain_extensions.output_parser.action_parser import ActionParser

from promts import CODER_PREFIX, REVIEWER_PREFIX, REVIEW
from tools import SendToReviewTool, ReviewTool, ApproveTool


def update_code(code: str, task: str, guidelines: str, requirements: str, max_reviews: int = 3) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    send_to_review_tool = SendToReviewTool()
    review_tool = ReviewTool()
    approve_tool = ApproveTool()

    code_to_improve = code
    review = ""
    for i in range(max_reviews):
        review = PromptTemplate.from_template(REVIEW).format_prompt(
            review=review).to_string() if review != "" else ""
        coder_instructions = PromptTemplate.from_template(CODER_PREFIX).format_prompt(
            task=task, guidelines=guidelines, requirements=requirements, review=review).to_string()
        reviewer_instructions = PromptTemplate.from_template(REVIEWER_PREFIX).format_prompt(
            task=task, guidelines=guidelines, requirements=requirements).to_string()
        output_parser = ActionParser()
        code_to_improve = initialize_agent(
            tools=[send_to_review_tool],  # + load_tools(["requests_get"])
            llm=llm,
            verbose=True,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            max_iterations=3,
            agent_kwargs={
                "system_message": coder_instructions,
                "output_parser": output_parser
            }
        )(dict(input=code_to_improve, chat_history=[]))["output"]

        reviewer_output = initialize_agent(
            tools=[review_tool, approve_tool],
            llm=llm,
            verbose=True,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            agent_kwargs={
                "system_message": reviewer_instructions,
                "output_parser": output_parser
            }
        )(dict(input=code_to_improve, chat_history=[]))
        if reviewer_output["tool_name"] == review_tool.name:
            review = reviewer_output["output"]
        elif reviewer_output["tool_name"] == approve_tool.name:
            return code_to_improve
        else:
            raise Exception("Unexpected reviewer output")
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
    updated_code = update_code(code=code, task=task, guidelines=guidelines, requirements=requirements)
    write_file(file_path=file_path, updated_code=updated_code)


if __name__ == '__main__':
    load_dotenv()
    main()
