from langchain_core.messages import HumanMessage
from typing import Any


from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode



from aiz.builders.provider_bulders import ProviderFactory
from aiz.tools.command_helper import CommandHelpTool
from aiz.agents.state import GlobalAgentState


def call_generator_model(state: GlobalAgentState, llm_with_tools) -> dict[str, Any]:
    """
    The primary "reasoning" node. It calls the LLM with the current
    conversation state and decides the next action.
    """
    print("--- Calling Generator LLM ---")
    
    messages = state["messages"]    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: GlobalAgentState) -> str:
    """
    The router or "conditional edge". It checks the last message in the state
    and decides where to go next.
    """
    print("--- Checking Agent State ---")
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        print(">>> Decision: Agent wants to use a tool.")
        return "continue_to_tools"
    else:
        print(">>> Decision: Agent has a final answer.")
        return "end_workflow"

def build_command_generation_agent(providers_config: dict):
    provider_factory = ProviderFactory()
    llm = provider_factory.build(providers_config)

    tools = [CommandHelpTool()]
    llm_with_tools = llm.bind_tools(tools)

    agent_node = lambda state: call_generator_model(state, llm_with_tools)


    workflow = StateGraph(GlobalAgentState)

    workflow.add_node("generator", agent_node)
    workflow.add_node("action", ToolNode(tools))


    workflow.set_entry_point("generator")
    workflow.add_conditional_edges(
        "generator",
        should_continue,
        {
            "continue_to_tools": "action",
            "end_workflow": END
        }
    )

    workflow.add_edge("action", "generator")

    app = workflow.compile()
    
    print("--- Agent Build Complete ---")
    return app