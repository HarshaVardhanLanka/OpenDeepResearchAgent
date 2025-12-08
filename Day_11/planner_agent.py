def planner_node(state, llm):
    topic = state['topic']
    search_mode = state.get('search_mode', 'General')
    
    # 1. Select Prompt based on Mode
    if search_mode == "Academic Papers":
        task_instruction = """
        Task: Generate 3 specific search queries to find **Scientific Research Papers, PDF Studies, and Academic Journals**.
        
        Guidelines:
        - Include keywords like 'arXiv', 'PDF', 'research paper', 'study', 'journal'.
        - Focus on finding distinct papers or methodologies.
        """
    else:
        task_instruction = """
        Task: Generate 3 distinct, specific search queries to gather comprehensive information.
        """

    # 2. Build Prompt
    prompt = f"""
    You are a Research Planner.
    Topic/Context: {topic}

    {task_instruction}

    Constraint: Return ONLY the 3 queries separated by newlines. Do not number them.
    """

    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.split('\n') if q.strip()]
    
    return {"research_plan": queries[:3]}