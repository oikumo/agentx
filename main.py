from dotenv import load_dotenv

from agent_x.ai.agent_tools.simple_tool import simple_tool
from agent_x.ai.chat.simple_chat import simple_chat_prompt_template
from agent_x.ai.llm.llms import get_local_llm_qwen2_5, get_llama_cpp_llm
from agent_x.ai.react_agents_tools.react_tools import react_tools
from agent_x.ai.react_search_agent.search_agent import search_agent
from agent_x.ai.router_agents.router_react_agent import router_agent
from agent_x.command_line import CommandLine
from agent_x.commands.commands import add
from agent_x.utils.utils import clear_console

load_dotenv()

if __name__ == "__main__":
    commands = {
        "cls": lambda _ : clear_console(),
        "q": lambda _ : print(f"QUIT COMMAND"),
        "h": lambda _ : print(f"HELP COMMAND"),
        "sum": lambda args : add(args),
        "router": lambda args: router_agent(),
        "chat": lambda args: simple_chat_prompt_template(
            llm = get_llama_cpp_llm()),
        "tool": lambda args: simple_tool(
            llm= get_local_llm_qwen2_5()),
        "rtool": lambda args: react_tools(
            llm=get_local_llm_qwen2_5()),
        "search": lambda args: search_agent(
            llm=get_local_llm_qwen2_5()
        )
    }

    commands_list = list(commands.keys())
    def print_commands():
        for command in commands_list:
            print(command)

    commands["list"] = lambda _ : print_commands()

    loop = CommandLine(commands)

    while True:
        loop.run()
