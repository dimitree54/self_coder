import re
from enum import Enum

from langchain.tools import BaseTool
from pydantic import BaseModel


def extract_code(input_string):
    # Detect code blocks
    pattern = r'```(?:python)?\s(.*?)```'
    match = re.search(pattern, input_string, re.DOTALL)

    if match:
        # Found code block
        code = match.group(1)
    else:
        # No code block, assume pure code
        code = input_string

    return code


class ToolType(Enum):
    RETURNING = "returning"
    FINAL = "final"
    DELEGATE = "delegate"


class SmartTool(BaseModel):
    tool: BaseTool
    tool_type: ToolType = ToolType.RETURNING


class ExtraThought(BaseModel):
    name: str
    description: str
