from langchain import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

from langchain_extension.tools_only_agent_with_thoughts.output_parser import ToolsOnlyOutputParser
from utils import IssueInfo
from promts import REVIEW, CODER_PREFIX, CODER_SUFFIX, TEMPLATE_TOOL_RESPONSE
from tools import SendToReviewTool, format_tools_description, format_tool_names


def improve_code(llm: ChatOpenAI, code_to_improve: str, issue_info: IssueInfo, review: str) -> str:
    review = PromptTemplate.from_template(REVIEW).format_prompt(
        review=review).to_string() if review != "" else ""
    send_to_review_tool = SendToReviewTool()
    output_parser = ToolsOnlyOutputParser(
        final_tools={send_to_review_tool.name},
        extra_thoughts=[
            ("first_thought", "string", "What is the best way to solve the task? What action to take with what action_input?"),
            ("criticism", "string", "Constructive criticism of the first_thought, considering an alternative options"),
            ("final_thought", "string", "Final reasoning, what action and action_input to choose and why"),
        ]
    )
    coder_agent_tools = [send_to_review_tool]  # + load_tools(["requests_get"])
    coder_agent = initialize_agent(
        tools=coder_agent_tools,
        llm=llm,
        verbose=True,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        max_iterations=1,
        agent_kwargs={
            "system_message": CODER_PREFIX,
            "human_message": CODER_SUFFIX,
            "template_tool_response": TEMPLATE_TOOL_RESPONSE,
            "output_parser": output_parser,
            "input_variables": [
                "input", "chat_history", "agent_scratchpad", "task", "guidelines", "requirements", "review",
                "format_instructions", "tools"]
        }
    )
    improved_code = coder_agent(dict(
        input=code_to_improve, chat_history=[], task=issue_info.task, guidelines=issue_info.guidelines,
        requirements=issue_info.requirements, review=review,
        tools=format_tools_description(coder_agent_tools),
        format_instructions=PromptTemplate.from_template(output_parser.get_format_instructions()).format(
            tool_names=format_tool_names(coder_agent_tools)
        )
    ))["output"]
    return improved_code
