from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.agents import initialize_agent, load_tools, AgentType
from langchain.chat_models import ChatOpenAI

from langchain_extension.tools_only_agent_with_thoughts.output_parser import ToolsOnlyWithThoughtsOutputParser
from promts import CODER_PREFIX, REVIEWER_PREFIX
from tools import SendToReviewTool, ReviewTool, ApproveTool


def update_code(code: str, task: str) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    send_to_review_tool = SendToReviewTool()
    coder_tools = load_tools(["requests_get"]) + [send_to_review_tool]
    coder_agent = initialize_agent(
        tools=coder_tools,
        llm=llm,
        verbose=True,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        max_iterations=3,
        agent_kwargs={
            "system_message": PromptTemplate.from_template(CODER_PREFIX).format_prompt(task=task).to_string(),
            "output_parser": ToolsOnlyWithThoughtsOutputParser()}
    )

    review_tool = ReviewTool()
    approve_tool = ApproveTool()
    reviewer_agent = initialize_agent(
        tools=[review_tool, approve_tool],
        llm=llm,
        verbose=True,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        agent_kwargs={
            "system_message": PromptTemplate.from_template(REVIEWER_PREFIX).format_prompt(task=task).to_string(),
            "output_parser": ToolsOnlyWithThoughtsOutputParser(final_tools={review_tool.name})}
    )

    send_to_review_tool.reviewer = reviewer_agent
    review_tool.coder = coder_agent

    coder_agent.run(input=code, chat_history=[], task=task)
    return send_to_review_tool.last_answer


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path: str, updated_code: str) -> None:
    with open(file_path, 'w') as file:
        file.write(updated_code)


def main():
    file_path = __file__
    task = input("Enter task: ")
    code = read_file(file_path=file_path)
    updated_code = update_code(code=code, task=task)
    write_file(file_path=file_path, updated_code=updated_code)


if __name__ == '__main__':
    load_dotenv()
    main()
