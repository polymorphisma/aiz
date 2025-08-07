from tools import CommandHelpTool


command_obj = CommandHelpTool()

value = command_obj.run("git")

print(value)
