def writer_node(state, llm):
    topic = state['topic']
    data = state['search_results']
    length = state.get('summary_length', 'Detailed')
    search_mode = state.get('search_mode', 'General Web')

    # --- 1. ACADEMIC MODE (Citations & Structure) ---
    if search_mode == "Academic Papers":
        role_desc = "You are an Academic Researcher writing a Literature Review."
        
        structure = """
        Structure:
        1. **Abstract**: Brief overview.
        2. **Literature Review**: Synthesize findings from the papers.
        3. **Methodologies**: Compare approaches found in the search data.
        4. **References**: STRICTLY format as a list of markdown links: - [Paper Title](URL). Use the URLs provided in the data.
        """
        citation_instruction = "IMPORTANT: You MUST use the URLs provided in the 'Verified Search Data' to create clickable links in the References section."

    # --- 2. GENERAL WEB MODE (Adaptive: Paragraph vs Report) ---
    else: 
        role_desc = "You are an articulate AI Assistant."
        
        structure = """
        ADAPTIVE FORMATTING INSTRUCTIONS:
        
        **SCENARIO A: Direct Question / Specific Follow-up**
        (e.g., "How does this compare to X?", "Explain the methodology", "Summarize this part")
        - Format: **Write exactly ONE single, comprehensive paragraph.**
        - Length: Target approximately **300 words**.
        - Content: Dive straight into the answer. Do not use Intro/Conclusion headers. Do not use bullet points. Flowing text only.
        
        **SCENARIO B: Broad Research Topic**
        (e.g., "The History of AI", "Global Warming Trends")
        - Format: Structured Report (Introduction, Key Findings, Conclusion).
        """
        
        citation_instruction = "Do NOT include a 'References' section. Do NOT include links. Just write a clean narrative."

    # --- 3. LENGTH LOGIC ---
    length_instruction = "Keep it concise." if length == "Short" else "Make it detailed."

    # --- 4. FINAL PROMPT ---
    prompt = f"""
    {role_desc}
    
    User Input: {topic}
    
    {structure}
    
    {citation_instruction}
    
    General Guideline: {length_instruction}
    
    CRITICAL FORMATTING RULE: Do NOT wrap the output in ```markdown or ``` code blocks. Return raw markdown text only.

    Verified Search Data:
    {data}
    """

    response = llm.invoke(prompt)
    
    # --- 5. CLEANUP (Force removal of code blocks) ---
    clean_content = response.content.replace('```markdown', '').replace('```', '').strip()
    
    return {"final_report": clean_content}