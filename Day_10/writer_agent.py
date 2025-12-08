def writer_node(state, llm):
    """
    Synthesizes the report based on the chosen length.
    """
    topic = state['topic']
    data = state['search_results']
    length = state.get('summary_length', 'Detailed') # Default to Detailed

    # 1. Define Prompts based on selection
    if length == "Short":
        instructions = """
        Task: Write a concise **Executive Summary** (approx 200 words).
        Style: Bullet points, direct, high-level overview.
        Structure:
        - Quick Summary
        - Top 3 Key Takeaways
        - Brief Conclusion
        """
    else:
        instructions = """
        Task: Write a **Comprehensive Deep-Dive Report** (approx 500 words).
        Style: Academic, detailed, professional.
        Structure:
        1. Introduction & Context
        2. Detailed Analysis of Findings
        3. Technical Nuances / Data comparison
        4. Strategic Implications
        5. Extensive Conclusion
        """

    # 2. Construct Final Prompt
    prompt = f"""
    You are a Senior Technical Writer.
    
    {instructions}

    Original Topic: {topic}
    
    Verified Research Data to use:
    {data}
    
    Format: Markdown.
    """

    response = llm.invoke(prompt)
    return {"final_report": response.content}