from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from langchain_extension.agent import Agent
from langchain_extension.utils import ToolType, SmartTool, ExtraThought
from promts import REVIEW, CODER_PREFIX
from tools import SendToReviewTool
from utils import IssueInfo


def improve_code(llm: ChatOpenAI, code_to_improve: str, issue_info: IssueInfo, review: str = "") -> str:
    code_improver = Agent(
        llm=llm,
        system_message=PromptTemplate.from_template(CODER_PREFIX),
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
            SmartTool(tool=SendToReviewTool(), tool_type=ToolType.FINAL)
        ],
        verbose=True
    )
    review = PromptTemplate.from_template(REVIEW).format_prompt(review=review).to_string() if review != "" else ""
    return code_improver.call(
        input=code_to_improve,
        chat_history=[],
        task=issue_info.task, guidelines=issue_info.guidelines,
        requirements=issue_info.requirements, review=review
    )
