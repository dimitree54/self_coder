import difflib
from typing import Optional

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from langchain_extension.tools_only_agent.agent import Agent
from langchain_extension.tools_only_agent.utils import ExtraThought, ToolType, SmartTool
from promts import REVIEWER_PREFIX
from tools import ReviewTool, ApproveTool
from utils import IssueInfo


def review_code(llm: ChatOpenAI, code_diff: str, issue_info: IssueInfo) -> Optional[str]:
    review_tool = ReviewTool()
    approve_tool = ApproveTool()
    code_reviewer = Agent(
        llm=llm,
        system_message=PromptTemplate.from_template(REVIEWER_PREFIX),
        extra_thoughts=[
            ExtraThought(
                name="first_thought",
                description="What is the best way to solve the task? What action to take with what action_input?"),
            ExtraThought(
                name="criticism",
                description="Constructive criticism of the first_thought, considering an alternative options"),
            ExtraThought(
                name="final_thought",
                description="Final reasoning, what action and action_input to choose and why"),
        ],
        tools=[
            SmartTool(tool=review_tool, tool_type=ToolType.FINAL),
            SmartTool(tool=approve_tool, tool_type=ToolType.FINAL)
        ],
        verbose=True
    )
    reviewer_output = code_reviewer.call(
        input=code_diff,
        chat_history=[],
        task=issue_info.task, guidelines=issue_info.guidelines,
        requirements=issue_info.requirements
    )

    if reviewer_output == approve_tool.approve_value:
        return None
    else:
        return reviewer_output


def get_diff(code_before: str, code_after: str) -> str:
    return "".join(difflib.unified_diff(code_before.splitlines(keepends=True), code_after.splitlines(keepends=True)))
