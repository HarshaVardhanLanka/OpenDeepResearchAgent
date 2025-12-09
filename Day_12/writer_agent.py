def writer_node(state, llm):
    topic = state['topic']
    data = state['search_results']
    length = state.get('summary_length', 'Detailed')
    search_mode = state.get('search_mode', 'General Web') # Default to General

    # 1. Define Logic based on Mode
    if search_mode == "Academic Papers":
        role_desc = "You are an Academic Researcher writing a Literature Review."
        
        structure = """
        Structure:
        1. **Abstract**: Brief overview.
        2. **Literature Review**: Synthesize findings from the papers.
        3. **Methodologies**: Compare approaches found in the search data.
        4. **References**: STRICTLY format as a list of markdown links: - [Paper Title](URL). Use the URLs provided in the data.
        """
        
        # Force citations for Academic mode
        citation_instruction = "IMPORTANT: You MUST use the URLs provided in the 'Verified Search Data' to create clickable links in the References section."

    else: # General Web
        role_desc = "You are a Senior Technical Writer."
        
        structure = """
        Structure:
        1. Introduction
        2. Key Findings
        3. Detailed Analysis
        4. Conclusion
        """
        
        # FORBID citations for General mode to keep it clean
        citation_instruction = "Do NOT include a 'References', 'Sources', or 'Bibliography' section. Do not include raw URLs or [Link] citations in the text. Just write a clean, flowing narrative."

    # 2. Define Length Logic
    length_instruction = "Keep it concise (approx 300 words)." if length == "Short" else "Make it comprehensive and detailed."

    # 3. Construct the Prompt
    prompt = f"""
    {role_desc}
    
    Task: Write a report on: {topic}
    {length_instruction}
    
    {structure}
    
    {citation_instruction}

    Verified Search Data:
    {data}
    
    Format: Markdown.
    """

    response = llm.invoke(prompt)
    return {"final_report": response.content}