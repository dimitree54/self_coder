from langchain_extension.tools_only_agent.utils import FinalAnswerTool
from utils import extract_code


class SendToReviewTool(FinalAnswerTool):
    name: str = "send_to_review"
    description: str = "When you ready to generate requested code, use that tool to send code to review. " \
                       "The input of that tool is your updated code without any additional text. " \
                       "Code should include whole updated file, including not changed lines. " \
                       "The code have to be executable, so do not include any non-code text."

    def _run(self, tool_input: str) -> str:
        return extract_code(tool_input)


class ReviewTool(FinalAnswerTool):
    name: str = "return_to_coder"
    description: str = "If there is a problem with code, use that tool to return code to coder with review. " \
                       "The input of that tool should be your review," \
                       " description of problems you found and suggestions how to fix them."


class ApproveTool(FinalAnswerTool):
    name: str = "approve"
    description: str = "If you are satisfied with code, use that tool to approve it. " \
                       "The input of that tool is your comments about code."
    return_direct: bool = True
    approve_value: str = "approved"

    def _run(self, tool_input: str) -> str:
        return self.approve_value
