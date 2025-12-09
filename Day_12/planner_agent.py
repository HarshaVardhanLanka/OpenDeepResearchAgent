def planner_node(state, llm):
    topic = state['topic']
    history = state.get('chat_history', '') # Get past chat
    search_mode = state.get('search_mode', 'General')
    
    # 1. Select Guidelines based on Mode
    if search_mode == "Academic Papers":
        mode_instruction = "Focus on finding Scientific Research Papers, PDF Studies, and Arxiv links."
    else:
        mode_instruction = "Focus on general comprehensive information from the web."

    # 2. Build Prompt with History
    prompt = f"""
    You are a Research Planner.
    
    CONTEXT (Previous Conversation):
    {history}

    CURRENT USER REQUEST: 
    {topic}

    Task: Based on the Current Request (and using Context to clarify references if needed), generate 3 specific search queries.
    {mode_instruction}

    Constraint: Return ONLY the 3 queries separated by newlines. Do not number them.
    """

    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.split('\n') if q.strip()]
    
    return {"research_plan": queries[:3]}