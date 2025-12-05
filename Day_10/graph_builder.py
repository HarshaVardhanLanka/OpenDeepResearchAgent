import os
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient

# Import our separate modules
from state import AgentState
from planner_agent import planner_node
from searcher_agent import searcher_node
from writer_agent import writer_node

def build_graph(google_api_key, tavily_api_key):
    """
    Initializes the LLM and Tools with the provided keys, 
    then builds the LangGraph workflow.
    """
    
    # 1. Setup Environment / Tools
    os.environ["GOOGLE_API_KEY"] = google_api_key
    llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", temperature=0.5)
    tavily = TavilyClient(api_key=tavily_api_key)

    # 2. Create Partial Functions
    # We inject the specific LLM/Tool instance into the node functions
    p_node = partial(planner_node, llm=llm)
    s_node = partial(searcher_node, tavily_client=tavily)
    w_node = partial(writer_node, llm=llm)

    # 3. Build Graph
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

    # 4. Compile
    return workflow.compile()