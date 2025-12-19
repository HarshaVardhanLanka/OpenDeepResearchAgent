def planner_node(state, llm):
    topic = state['topic']
    history = state.get('chat_history', '') 
    search_mode = state.get('search_mode', 'General')
    
    # Define instructions based on mode
    if search_mode == "Academic Papers":
        mode_instruction = "Focus on Scientific Research Papers, PDF Studies, and Arxiv."
    else:
        mode_instruction = "Focus on general comprehensive information from the web."

    prompt = f"""
    You are a Research Planner.
    
    PREVIOUS CONVERSATION:
    {history}

    CURRENT USER REQUEST: 
    {topic}

    # ==================================================
    # 🧠 LOGIC: CONTEXT AWARENESS vs. NEW TOPIC
    # ==================================================
    Analyze the CURRENT USER REQUEST in relation to the PREVIOUS CONVERSATION.
    
    **CASE 1: FOLLOW-UP (Related)**
    (e.g., "tell me more", "what about the costs?", "explain that", "summarize the second paper")
    -> ACTION: Use the PREVIOUS CONVERSATION to clarify context.

    **CASE 2: NEW TOPIC (Unrelated)**
    (e.g., Previous was about "Quantum Physics", Current is "Best Pizza in NY")
    -> ACTION: **COMPLETELY IGNORE** the PREVIOUS CONVERSATION. Treat this as a fresh start. Do not generate queries that mix the two topics.

    # ==================================================
    # TASK
    # ==================================================
    Based on the logic above, generate 3 specific search queries.
    {mode_instruction}

    Constraint: Return ONLY the 3 queries separated by newlines. Do not number them.
    """

    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.split('\n') if q.strip()]
    
    return {"research_plan": queries[:3]}