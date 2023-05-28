import difflib
from typing import Optional

from langchain import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

from langchain_extension.tools_only_agent_with_thoughts.output_parser import ToolsOnlyOutputParser
from utils import IssueInfo
from promts import REVIEWER_PREFIX
from tools import ReviewTool, ApproveTool


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
            "output_parser": ToolsOnlyOutputParser(final_tools={review_tool.name, approve_tool.name})}
    )(dict(input=code_diff, chat_history=[]))
    if reviewer_output["tool_name"] == review_tool.name:
        return reviewer_output["output"]
    elif reviewer_output["tool_name"] == approve_tool.name:
        return None
    else:
        raise Exception("Unexpected reviewer output")


def get_diff(code_before: str, code_after: str) -> str:
    return "".join(difflib.unified_diff(code_before.splitlines(keepends=True), code_after.splitlines(keepends=True)))
