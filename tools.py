from typing import List

from langchain.tools import BaseTool


class FinalAnswerTool(BaseTool):
    """Tool for direct returning its arguments from agent (use it as final_tool in ToolsOnlyWithThoughtsOutputParser)"""

    def _run(self, tool_input: str) -> str:
        raise RuntimeError("That tool supposed to be final. Add it as final_tool in ToolsOnlyWithThoughtsOutputParser.")

    async def _arun(self, tool_input: str) -> str:
        raise RuntimeError("That tool supposed to be final. Add it as final_tool in ToolsOnlyWithThoughtsOutputParser.")


class SendToReviewTool(FinalAnswerTool):
    name: str = "send_to_review"
    description: str = "When you ready to generate requested code, use that tool to send code to review. " \
                       "The input of that tool is your updated code without any additional text. " \
                       "Code should include whole updated file, including not changed lines. " \
                       "The code have to be executable, so do not include any non-code text."


class ReviewTool(FinalAnswerTool):
    name: str = "return_to_coder"
    description: str = "If there is a problem with code, use that tool to return code to coder with review. " \
                       "The input of that tool should be your review," \
                       " description of problems you found and suggestions how to fix them."


class ApproveTool(FinalAnswerTool):
    name: str = "Approve"
    description: str = "If you are satisfied with code, use that tool to approve it. " \
                       "The input of that tool is your comments about code."
    return_direct: bool = True


def format_tools_description(tools: List[BaseTool]) -> str:
    return "\n".join(
        [f"> {tool.name}: {tool.description}" for tool in tools]
    )


def format_tool_names(tools: List[BaseTool]) -> str:
    return ", ".join([tool.name for tool in tools])
