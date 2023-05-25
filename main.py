from pathlib import Path

import difflib
from typing import Optional

from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel

from langchain_extension.tools_only_agent_with_thoughts.output_parser import ToolsOnlyWithThoughtsOutputParser
from promts import CODER_PREFIX, REVIEWER_PREFIX, REVIEW, TEMPLATE_TOOL_RESPONSE, CODER_SUFFIX
from tools import SendToReviewTool, ReviewTool, ApproveTool, format_tools_description, format_tool_names


class IssueInfo(BaseModel):
    task: str
    guidelines: str
    requirements: str


def improve_code(llm: ChatOpenAI, code_to_improve: str, issue_info: IssueInfo, review: str) -> str:
    review = PromptTemplate.from_template(REVIEW).format_prompt(
        review=review).to_string() if review != "" else ""
    send_to_review_tool = SendToReviewTool()
    output_parser = ToolsOnlyWithThoughtsOutputParser(final_tools={send_to_review_tool.name})
    coder_agent_tools = [send_to_review_tool]  # + load_tools(["requests_get"])
    coder_agent = initialize_agent(
        tools=coder_agent_tools,
        llm=llm,
        verbose=True,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        max_iterations=1,
        agent_kwargs={
            "system_message": CODER_PREFIX,
            "human_message": CODER_SUFFIX,
            "template_tool_response": TEMPLATE_TOOL_RESPONSE,
            "output_parser": output_parser,
            "input_variables": [
                "input", "chat_history", "agent_scratchpad", "task", "guidelines", "requirements", "review",
                "format_instructions", "tools"]
        }
    )
    improved_code = coder_agent(dict(
        input=code_to_improve, chat_history=[], task=issue_info.task, guidelines=issue_info.guidelines,
        requirements=issue_info.requirements, review=review,
        tools=format_tools_description(coder_agent_tools),
        format_instructions=PromptTemplate.from_template(output_parser.get_format_instructions()).format(
            tool_names=format_tool_names(coder_agent_tools)
        )
    ))["output"]
    return improved_code


def review_code(llm: ChatOpenAI, code_diff: str, issue_info: IssueInfo) -> Optional[str]:
    review_tool = ReviewTool()
    approve_tool = ApproveTool()
    reviewer_instructions = PromptTemplate.from_template(REVIEWER_PREFIX).format_prompt(
        task=issue_info.task, guidelines=issue_info.guidelines, requirements=issue_info.requirements).to_string()

    reviewer_output = initialize_agent(
        tools=[review_tool, approve_tool],
        llm=llm,
        verbose=True,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        agent_kwargs={
            "system_message": reviewer_instructions,
            "output_parser": ToolsOnlyWithThoughtsOutputParser(final_tools={review_tool.name, approve_tool.name})}
    )(dict(input=code_diff, chat_history=[]))
    if reviewer_output["tool_name"] == review_tool.name:
        return reviewer_output["output"]
    elif reviewer_output["tool_name"] == approve_tool.name:
        return None
    else:
        raise Exception("Unexpected reviewer output")


def get_diff(code_before: str, code_after: str) -> str:
    return "".join(difflib.unified_diff(code_before.splitlines(keepends=True), code_after.splitlines(keepends=True)))


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
