
import asyncio
from dotenv import load_dotenv
import os

from aiz.agents.supervisor import build_supervisor_agent
from langchain_core.messages import HumanMessage

load_dotenv()



async def run_supervisor_test():
    """
    Builds and runs the SUPERVISOR agent for a test query.
    """
    aws_bedrock_config = {
        "provider": "aws_bedrock", 
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "region_name": "us-east-1",
        "temperature": 0.0,
    }

    supervisor_runnable = build_supervisor_agent(aws_bedrock_config)

    user_query = "IN my currnet project i want to add changes commit and using gh create pr against main branch?"

    # --- THIS IS THE FIX ---
    initial_state = {
        # The first message in the history IS the user's question.
        "messages": [HumanMessage(content=user_query)], 
        "user_query": user_query, # We still keep this for reference
    }
    
    config = {"configurable": {"thread_id": "supervisor-test-1"}}
    final_state = None

    print("\n--- Invoking SUPERVISOR Agent ---")
    async for event in supervisor_runnable.astream_events(initial_state, config, version="v2"):
        kind = event["event"]
        print(event)
        print("----")

        if kind == "on_chain_end" and event["name"] == "LangGraph":
            final_state = event["data"].get("output")

    print("\n--- Final Output from Supervisor ---")
    if final_state:
        final_answer = final_state['messages'][-1].content
        print(final_answer)
    else:
        print("Could not determine final state.")


if __name__ == "__main__":
    asyncio.run(run_supervisor_test())
