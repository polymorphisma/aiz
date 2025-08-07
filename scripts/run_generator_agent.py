import asyncio
from dotenv import load_dotenv
import os

from aiz.agents.command_generator import build_command_generation_agent
from langchain_core.messages import HumanMessage, SystemMessage
from aiz.prompts.generator_prompts import COMMAND_GENERATOR_SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

async def run_test():
    """
    Builds and runs the CommandGenerationAgent for a test query.
    """
    # 1. Define the model configuration to use
    aws_bedrock_config = {
    "provider": "aws_bedrock", 
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0", # A great, balanced choice
    "region_name": "us-east-1", # Or whichever region you use for Bedrock
    "temperature": 0.1,
    "max_tokens": 2048,
}

    # 2. Build our agent runnable
    agent_runnable = build_command_generation_agent(aws_bedrock_config)

    # 3. Define the initial state for the workflow
    user_query = "How do i push commit to the git?"
    
    initial_state = {
        "messages": [
            SystemMessage(content=COMMAND_GENERATOR_SYSTEM_PROMPT),
            HumanMessage(content=user_query)
        ],
        "user_query": user_query,
        "target_cli_tool": "git"
    }
    
    config = {"configurable": {"thread_id": "test-thread-1"}}
    final_state = None

    print("\n--- Invoking Agent ---")
    async for event in agent_runnable.astream_events(initial_state, config, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="")
        elif kind == "on_tool_start":
            print("--")
            print(f"Tool Start: {event['name']} with args {event['data'].get('input')}")
        elif kind == "on_tool_end":
            tool_output = event['data'].get('output')
            if tool_output:
                # Access the .content attribute of the ToolMessage object
                print(f"Tool Output: {tool_output.content[:200]}...")
        elif kind == "on_chain_end" and event["name"] == "LangGraph":
            print("\n--- Graph Execution Finished ---")
            final_state = event["data"].get("output")

    if final_state:
        final_answer = final_state['messages'][-1].content
        print(f"Final Generated Command: {final_answer}")
    else:
        print("Could not determine final state.")

if __name__ == "__main__":
    asyncio.run(run_test())