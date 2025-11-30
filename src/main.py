from dotenv import load_dotenv

from ai.agent_tools.simple_tool import simple_tool
from ai.chat.simple_chat import simple_chat_prompt_template
from ai.llm.llms import get_local_llm_qwen3, get_local_llm_qwen2_5, get_remote_llm_openai_gpt3_5_turbo, \
    get_local_llm_qwen2_5_coder, get_llama_cpp_llm
from ai.react_agents_tools.react_tools import react_tools
from ai.router_agents.router_react_agent import router_agent
from src.command_line import CommandLine
from src.commands.commands import add
from src.utils.utils import clear_console

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
            llm=get_local_llm_qwen2_5())
    }

    loop = CommandLine(commands)

    while True:
        loop.run()
