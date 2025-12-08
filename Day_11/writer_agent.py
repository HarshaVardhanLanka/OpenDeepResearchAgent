def writer_node(state, llm):
    topic = state['topic']
    data = state['search_results']
    length = state.get('summary_length', 'Detailed')
    search_mode = state.get('search_mode', 'General')

    # 1. Define Style based on Mode
    if search_mode == "Academic Papers":
        role_desc = "You are an Academic Researcher writing a Literature Review."
        structure = """
        Structure:
        1. **Abstract**: Brief overview of the topic.
        2. **Key Research Papers**: Summarize the specific papers/studies found in the data. Mention authors/dates if available.
        3. **Methodologies & Findings**: What did the researchers find?
        4. **References**: List the sources/URLs provided in the search data.
        """
    else:
        role_desc = "You are a Senior Technical Writer."
        structure = """
        Structure:
        1. Introduction
        2. Key Findings
        3. Analysis
        4. Conclusion
        """

    # 2. Define Length logic (Short vs Long)
    length_instruction = "Keep it concise (approx 300 words)." if length == "Short" else "Make it comprehensive and detailed."

    # 3. Final Prompt
    prompt = f"""
    {role_desc}
    
    Task: Write a report on: {topic}
    {length_instruction}
    
    {structure}

    Verified Search Data (Use this for citations):
    {data}
    
    Format: Markdown.
    """

    response = llm.invoke(prompt)
    return {"final_report": response.content}