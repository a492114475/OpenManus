from pydantic import Field
import asyncio
from app.agent.toolcall import ToolCallAgent
from app.prompt.WIT import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.evaluator import Evaluator
from app.tool.exp_IV import ExpIv
from app.tool.file_saver import FileSaver
from app.tool.folder_reader import FolderReader
from app.tool.google_search import GoogleSearch
from app.tool.path_generator import PathGenerator
from app.tool.python_execute import PythonExecute
from app.tool.performing_generation import PerformingGeneration


class WIT_agent(ToolCallAgent):
    """
    A versatile general-purpose agent that uses planning to solve various tasks.

    This agent extends PlanningAgent with a comprehensive set of tools and capabilities,
    including Python execution, web browsing, file operations, and information retrieval
    to handle a wide range of user requests.
    """

    name: str = "WIT"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PerformingGeneration(), Evaluator(), Terminate(),
            PathGenerator(),
            FolderReader(),
            ExpIv(),
            FileSaver(),
        )
    )


from app.logger import logger


async def main():
    agent = WIT_agent()
    while True:
        try:
            prompt = input("Enter your prompt (or 'exit'/'quit' to quit): ")
            prompt_lower = prompt.lower()
            if prompt_lower in ["exit", "quit"]:
                logger.info("Goodbye!")
                break
            if not prompt.strip():
                logger.warning("Skipping empty prompt.")
                continue
            logger.warning("Processing your request...")
            await agent.run(prompt)
        except KeyboardInterrupt:
            logger.warning("Goodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
