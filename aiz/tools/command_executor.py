import subprocess
from typing import Type
from pydantic import BaseModel, Field

from langchain_core.tools import BaseTool

from rich.console import Console
from rich.prompt import Confirm

# You can keep CommandInput as it's the same shape, or create a new one for clarity.
class ExecutorInput(BaseModel):
    """Input for the command executor tool."""
    command: str = Field(description="The shell command string to execute.")

class CommandExecutorTool(BaseTool):
    """A tool to execute a shell command after user confirmation."""
    name: str = "command_executor"
    description: str = "Executes a shell command after receiving user confirmation. Use this as the final step."
    args_schema: Type[BaseModel] = ExecutorInput

    def _run(self, command: str) -> str:
        """Use the tool synchronously."""
        console = Console()
        console.print(f"\n[yellow]Proposed command:[/yellow]\n[bold cyan]$ {command}[/bold cyan]")
        
        if Confirm.ask("[bold]Do you want to execute this command?[/bold]", default=False, show_default=True):
            try:
                # Use shell=True for simplicity here, but be aware of security implications
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60
                )
                output = result.stdout if result.stdout else "Command executed successfully with no output."
                return output
            except subprocess.CalledProcessError as e:
                return f"Error executing command:\n{e.stderr}"
            except subprocess.TimeoutExpired:
                return f"Error: The command '{command}' timed out."
        else:
            return "Execution cancelled by user."


    async def _arun(self, command: str) -> str:
        """Use the tool asynchronously."""
        # The async version is trickier because standard input() is blocking.
        # A simple approach for now:
        return self._run(command)
    

if __name__ == "__main__":
    obj = CommandExecutorTool()
    value = obj.run('git status')
    print("-" * 100)
    print(value)