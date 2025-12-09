import os
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI  # <--- CHANGED FROM GOOGLE
from tavily import TavilyClient

# Import our separate modules
from state import AgentState
from planner_agent import planner_node
from searcher_agent import searcher_node
from writer_agent import writer_node

def build_graph(openrouter_api_key, tavily_api_key):
    """
    Initializes the LLM via OpenRouter and builds the graph.
    """
    
    # 1. Setup OpenRouter LLM
    # We use "google/gemini-2.0-flash-001" as it is fast and powerful.
    # You can change this string to "openai/gpt-4o-mini" or others on OpenRouter.
    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001", 
        openai_api_key=openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.5
    )

    # 2. Setup Tavily
    tavily = TavilyClient(api_key=tavily_api_key)

    # 3. Create Partial Functions
    p_node = partial(planner_node, llm=llm)
    s_node = partial(searcher_node, tavily_client=tavily)
    w_node = partial(writer_node, llm=llm)

    # 4. Build Graph
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("planner", p_node)
    workflow.add_node("searcher", s_node)
    workflow.add_node("writer", w_node)

    # Add Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "writer")
    workflow.add_edge("writer", END)

    # 5. Compile
    return workflow.compile()