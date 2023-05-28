from typing import List, Any

from langchain import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

from pydantic import BaseModel

from langchain_extension.tools_only_agent.output_parser import ToolsOnlyOutputParser
from langchain_extension.tools_only_agent.utils import ToolType, SmartTool, ExtraThought, format_tool_names, \
    format_tools_description
from langchain_extension.tools_only_agent.prompt import TEMPLATE_TOOL_RESPONSE, TOOLS_AND_FORMAT, SUFFIX


class Agent(BaseModel):
    llm: ChatOpenAI
    system_message: PromptTemplate
    extra_thoughts: List[ExtraThought] = []
    tools: List[SmartTool] = []
    verbose: bool = False

    def call(self, **kwargs) -> dict[str, Any]:
        # we initialize new agent every call to support dynamically changing tools
        output_parser = ToolsOnlyOutputParser(
            final_tools=set([tool.tool.name for tool in self.tools if tool.tool_type == ToolType.FINAL]),
            extra_thoughts=self.extra_thoughts
        )
        tools = [tool.tool for tool in self.tools]
        tools_and_format_instructions = PromptTemplate.from_template(TOOLS_AND_FORMAT).format(
            tools=format_tools_description(tools),
            format_instructions=PromptTemplate.from_template(output_parser.get_format_instructions()).format(
                tool_names=format_tool_names(tools)
            )
        )
        agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            verbose=self.verbose,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            max_iterations=1,
            agent_kwargs={
                "system_message": self._format_prompt(self.system_message, **kwargs) + tools_and_format_instructions,
                "human_message": SUFFIX,
                "template_tool_response": TEMPLATE_TOOL_RESPONSE,
                "output_parser": output_parser
            }
        )
        return agent(kwargs)

    @staticmethod
    def _format_prompt(prompt: PromptTemplate, **kwargs) -> str:
        relevant_args = {key: value for key, value in kwargs.items() if key in prompt.input_variables}
        return prompt.format(**relevant_args)
