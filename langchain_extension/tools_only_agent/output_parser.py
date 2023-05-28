from typing import Union, Set, List

from langchain import PromptTemplate
from langchain.agents.conversational_chat.output_parser import ConvoOutputParser
from langchain.schema import AgentAction, AgentFinish

from langchain_extension.tools_only_agent.utils import ExtraThought
from langchain_extension.tools_only_agent.prompt import FORMAT_INSTRUCTIONS


class ToolsOnlyOutputParser(ConvoOutputParser):
    final_tools: Set[str] = set()
    extra_thoughts: List[ExtraThought] = []

    def format_extra_thoughts(self) -> str:
        if len(self.extra_thoughts) == 0:
            return ""
        return "\n\t".join([
            f'"{thought.name}": string [{thought.description}]' for thought in self.extra_thoughts]) + "\n\t"

    def get_format_instructions(self) -> str:
        extra_thoughts_string = self.format_extra_thoughts()
        format_instructions = PromptTemplate.from_template(FORMAT_INSTRUCTIONS).format_prompt(
            extra_thoughts=extra_thoughts_string, tool_names="{tool_names}").to_string()
        return format_instructions

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        action: AgentAction = super().parse(text)
        if action.tool in self.final_tools:
            return AgentFinish({"output": action.tool_input, "tool_name": action.tool}, text)
        return action
