from typing import Union, Set

from langchain.agents.conversational_chat.output_parser import ConvoOutputParser
from langchain.schema import AgentAction, AgentFinish

from langchain_extension.tools_only_agent_with_thoughts.prompt import FORMAT_INSTRUCTIONS


class ToolsOnlyWithThoughtsOutputParser(ConvoOutputParser):
    final_tools: Set[str] = set()

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        action: AgentAction = super().parse(text)
        if action.tool in self.final_tools:
            return AgentFinish({"output": action.tool_input, "tool_name": action.tool}, text)
        return action
