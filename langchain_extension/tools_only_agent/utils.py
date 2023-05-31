from enum import Enum
from typing import List

from langchain.tools import BaseTool
from pydantic import BaseModel


class ToolType(Enum):
    RETURNING = "returning"  # simple tool, returning its output back to agent
    FINAL = "final"  # tool, replacing FinalAnswer of agent. Output of that tool will be returned as output of the agent
    DELEGATE = "delegate"  # tool, which will answer to agent's caller instead of agent


class SmartTool(BaseModel):
    tool: BaseTool
    tool_type: ToolType = ToolType.RETURNING


class ExtraThought(BaseModel):
    name: str
    description: str


def format_tool_names(tools: List[BaseTool]) -> str:
    return ", ".join([tool.name for tool in tools])


class FinalAnswerTool(BaseTool):
    """Tool for direct returning its arguments from agent (use it as final_tool in ToolsOnlyOutputParser)"""

    def _run(self, tool_input: str) -> str:
        return tool_input

    async def _arun(self, tool_input: str) -> str:
        return self._run(tool_input)


def format_tools_description(tools: List[BaseTool]) -> str:
    return "\n".join(
        [f"> {tool.name}: {tool.description}" for tool in tools]
    )
