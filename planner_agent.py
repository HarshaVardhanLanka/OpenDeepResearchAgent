def planner_node(state, llm):
    """
    Analyzes the request and creates search queries.
    Args:
        state: AgentState
        llm: The initialized ChatGoogleGenerativeAI instance
    """
    topic = state['topic']
    
    prompt = f"""
    You are a Research Planner.
    Topic/Context: {topic}

    Task: Generate 3 distinct, specific search queries to gather comprehensive information.
    Constraint: Return ONLY the 3 queries separated by newlines. Do not number them.
    """

    response = llm.invoke(prompt)
    
    # Process output into a list
    queries = [q.strip() for q in response.content.split('\n') if q.strip()]
    
    return {"research_plan": queries[:3]}