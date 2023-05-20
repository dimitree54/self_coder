from typing import Optional, Callable

from langchain import PromptTemplate
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool

from langchain_extension.utils import extract_code


class SendToReviewTool(BaseTool):
    """Use other agent as tool. You can specify reviewer later to make recursive agent calls possible."""
    reviewer: Optional[AgentExecutor] = None
    tool_input_preprocessing: Optional[Callable[[str], str]] = None

    name: str = "send_to_review"
    description: str = "When you ready to generate requested code, use that tool to send code to review. " \
                       "The input of that tool should be your code without any additional text. " \
                       "The code have to be executable, so do not include any non-code text."
    last_answer: Optional[str] = None

    def _run(self, tool_input: str) -> str:
        if self.reviewer is None:
            raise ValueError("Agent executor is not initialized")
        processed_tool_input = extract_code(tool_input)
        answer = self.reviewer.run(input=processed_tool_input, chat_history=[])
        self.last_answer = answer
        return answer

    async def _arun(self, tool_input: str) -> str:
        if self.reviewer is None:
            raise ValueError("Agent executor is not initialized")
        processed_tool_input = extract_code(tool_input)
        answer = await self.reviewer.arun(input=processed_tool_input, chat_history=[])
        self.last_answer = answer
        return answer


class ReviewTool(BaseTool):
    coder: Optional[AgentExecutor] = None
    name: str = "return_to_coder"
    description: str = "If there is a problem with code, use that tool to return code to coder with review. " \
                       "The input of that tool should be your review," \
                       " description of problems you found and suggestions how to fix them."

    def _run(self, tool_input: str) -> str:
        raise Exception("Review tool should not be used directly")

    async def _arun(self, tool_input: str) -> str:
        raise Exception("Review tool should not be used directly")


class ApproveTool(BaseTool):
    name: str = "Approve"
    description: str = "If you are satisfied with code, use that tool to approve it. " \
                       "The input of that tool is your comments about code."
    return_direct: bool = True

    def _run(self, tool_input: str) -> str:
        return ""

    async def _arun(self, tool_input: str) -> str:
        return ""
