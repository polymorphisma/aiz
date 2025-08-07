from langchain_core.tools import Tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage




from aiz.agents.state import GlobalAgentState
from aiz.builders.provider_bulders import ProviderFactory
from aiz.prompts.supervisor_prompts import SUPERVISOR_SYSTEM_PROMPT
from aiz.prompts.generator_prompts import COMMAND_GENERATOR_SYSTEM_PROMPT
from aiz.agents.command_generator import build_command_generation_agent, should_continue

from aiz.tools.command_executor import CommandExecutorTool


def create_generator_agent_tool(provider_config: dict) -> Tool:
    """
    This function builds the CommandGenerationAgent and wraps it as a Tool
    for the Supervisor to use.
    """
    print("--- Building Specialist: CommandGenerator Agent ---")
    generator_agent_runnable = build_command_generation_agent(provider_config)

    def _invoke_worker_agent(user_query: str) -> str:
        """A wrapper function to transform the input and extract the output."""
        print(f"--- Specialist agent receiving query: {user_query} ---")
        
        # 1. Construct the correct initial state for the worker
        initial_state = {
            "messages": [
                ("system", COMMAND_GENERATOR_SYSTEM_PROMPT),
                ("user", user_query)
            ],
            "user_query": user_query,
            "target_cli_tool": "tbd" # Worker will figure this out now
        }
        
        # 2. Invoke the worker agent
        final_state = generator_agent_runnable.invoke(
            initial_state, 
            config={"configurable": {"thread_id": f"worker-session-{user_query[:10]}"}}
        )
        
        # 3. Extract and return just the final command string
        return final_state['messages'][-1].content

    async def _ainvoke_worker_agent(user_query: str) -> str:
        """Async version of the wrapper."""
        print(f"--- Specialist agent receiving query (async): {user_query} ---")
        initial_state = {
            "messages": [
                ("system", COMMAND_GENERATOR_SYSTEM_PROMPT),
                ("user", user_query)
            ],
            "user_query": user_query,
            "target_cli_tool": "tbd"
        }
        final_state = await generator_agent_runnable.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": f"worker-session-{user_query[:10]}"}}
        )
        return final_state['messages'][-1].content

    generator_tool = Tool(
        name="command_generator_specialist",
        description=(
            "Use this specialist agent to generate a precise shell command. "
            "The input must be the user's full, original objective."
        ),
        # Use our new wrapper functions
        func=_invoke_worker_agent,
        coroutine=_ainvoke_worker_agent
    )

    return generator_tool


def format_final_output(state: GlobalAgentState) -> dict:
    """
    This node's only job is to prepare the clean, final output for the user.
    """
    print("--- Formatting Final Output ---")
    # Get the result from the last tool call (the executor)
    last_message = state['messages'][-1]
    
    if isinstance(last_message, ToolMessage) and last_message.name == "command_executor":
        command_result = last_message.content
        # We return the raw command output as the final answer
        return {"final_answer": command_result}
    
    # Fallback in case something went wrong
    return {"final_answer": "Workflow complete, but could not determine final command output."}


def call_supervisor_model(state, llm_with_tools):
    """
    Calls the supervisor LLM with the full message history.
    The system prompt is prepended to ensure it always has its instructions.
    """
    print("--- Calling Supervisor LLM ---")
    
    # Prepend the system prompt to the current message state
    messages = [("system", SUPERVISOR_SYSTEM_PROMPT)] + state["messages"]
    
    # Invoke the LLM
    response = llm_with_tools.invoke(messages)
    
    # Return only the new AI message to be appended to the state
    return {"messages": [response]}

# We need a more sophisticated router now
def supervisor_router(state: GlobalAgentState) -> str: # Return type is string
    """The router for the supervisor agent."""
    last_message = state['messages'][-1]
    
    if last_message.tool_calls:
        return "action"
    
    if isinstance(last_message, ToolMessage) and last_message.name == "command_executor":
        return "final_output"
    
    # If the LLM has just given a conversational response with no tool calls,
    # it means the workflow is finished.
    return "end" # Return the string 'end'

def build_supervisor_agent(provider_config: dict):
    """
    Builds the main Supervisor agent that orchestrates other agents.
    """
    print("--- Building Orchestrator: Supervisor Agent ---")
    
    generator_agent_as_tool = create_generator_agent_tool(provider_config)
    supervisor_tools = [generator_agent_as_tool, CommandExecutorTool()]

    factory = ProviderFactory()

    supervisor_llm = factory.build(provider_config) 
    llm_with_supervisor_tools = supervisor_llm.bind_tools(supervisor_tools)
    
    workflow = StateGraph(GlobalAgentState)
    
    supervisor_node = lambda state: call_supervisor_model(state, llm_with_supervisor_tools)

    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("action", ToolNode(supervisor_tools))
    workflow.add_node("final_output", format_final_output) # <-- ADD NEW NODE

    workflow.set_entry_point("supervisor")


    # Use the new router
    workflow.add_conditional_edges("supervisor", supervisor_router, {
        "action": "action",
        "final_output": "final_output",
        "end": END  # <-- ADD THIS MAPPING
    })

    workflow.add_edge("action", "supervisor") # The loop remains
    workflow.add_edge("final_output", END) # The formatter is the true end

    # 5. Compile and return the final orchestrator app
    app = workflow.compile()
    print("--- Supervisor Build Complete ---")
    return app