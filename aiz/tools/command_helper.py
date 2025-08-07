import subprocess
import asyncio
import logging
from typing import Type
from pydantic import BaseModel, Field
import shlex
from langchain.tools import BaseTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class CommandInput(BaseModel):
    """Input for the command help tool."""
    command: str = Field(description="The command-line tool to get help for.")

class CommandHelpTool(BaseTool):
    """A tool to get the help documentation for a command-line utility."""
    name: str = "command_help"
    description: str = "Useful for getting the --help output of a command-line tool."
    args_schema: Type[BaseModel] = CommandInput

    def _run(self, command: str) -> str:
        """Use the tool synchronously."""
        logger.info(f"Running synchronous help lookup for command: '{command}'")
        try:
            command_parts = shlex.split(command)
            
            result = subprocess.run(
                [*command_parts, "--help"], # Unpack the list of parts
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            logger.info(f"Successfully retrieved sync help output for command: '{command}'")
            return result.stdout
        except FileNotFoundError:
            error_msg = f"The command '{command}' was not found."
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except subprocess.CalledProcessError as e:
            logger.warning(f"Command '{command}' returned a non-zero exit code.")
            if e.stderr:
                logger.debug("Using stderr as help output.")
                return e.stderr
            return f"Error executing command: {e}"
        except subprocess.TimeoutExpired:
            error_msg = f"The command '{command}' timed out."
            logger.error(error_msg)
            return f"Error: {error_msg}"

    async def _arun(self, command: str) -> str:
        """Use the tool asynchronously."""
        logger.info(f"Running asynchronous help lookup for command: '{command}'")
        try:
            command_parts = shlex.split(command)

            proc = await asyncio.create_subprocess_exec(
                *command_parts, # Unpack the list here as well
                "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.info(f"Successfully retrieved async help output for command: '{command}'")
                return stdout.decode()
            else:
                # The LLM often learns more from the error message than just a "not found".
                # It's better to return the actual stderr from the command if it exists.
                output = stderr.decode() if stderr else stdout.decode()
                logger.warning(f"Async command '{command}' failed. Output: {output}")
                return output

        except FileNotFoundError:
            error_msg = f"The command '{shlex.split(command)[0]}' was not found."
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            logger.exception(f"Unexpected error while running command '{command}': {e}")
            return f"An unexpected error occurred: {e}"


# Example of using it asynchronously
async def main():
    help_tool = CommandHelpTool()
    print("\n--- Async Help for python ---")
    async_help_text = await help_tool.arun("git")
    print(async_help_text)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())