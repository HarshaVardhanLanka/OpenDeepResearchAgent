def writer_node(state, llm):
    topic = state['topic']
    data = state['search_results']
    length = state.get('summary_length', 'Detailed')
    search_mode = state.get('search_mode', 'General Web')

    # --- 0. DEFINE LENGTH INSTRUCTION FOR SCENARIO B ONLY ---
    if length == "Short":
        b_length_instruction = "Length Constraint: Target approximately 500 words. Be concise but cover the main points."
    else:
        b_length_instruction = "Length Constraint: Target approximately 800 words. Provide a comprehensive, deep-dive analysis."

    # --- 1. ACADEMIC MODE ---
    if search_mode == "Academic Papers":
        role_desc = "You are an Academic Researcher writing a Literature Review."
        
        structure = f"""
        ADAPTIVE FORMATTING INSTRUCTIONS - ANALYZE THE INPUT:
        
        **SCENARIO A: Direct Question / Specific Follow-up**
        (e.g., "How does this compare to X?", "Explain the methodology","Explain the Literature Review", "Summarize this part")
        - Format: **Write exactly ONE single, comprehensive paragraph.**
        - Length: Target approximately **300 words**. (IGNORE user's '{length}' setting; always write ~300 words here).
        - Content: Dive straight into the answer. Do not use Intro/Conclusion headers. Flowing text only.
        - **Citations:** Do **NOT** include a References section or links for this short answer.
        
        **SCENARIO B: Broad Research Topic**
        (e.g., "Literature review on LLMs", "History of Quantum Computing")
        - Format: **Full Academic Report**.
        - Guideline: {b_length_instruction}
        - Structure:
          1. **Abstract**: Brief overview.
          2. **Literature Review**: Synthesize findings from the papers.
          3. **Methodology**: Compare approaches found in the search data.
          4. **References**: STRICTLY format as a list of markdown links: - [Paper Title](URL). Use the URLs provided in the data.
        """
        
        citation_instruction = "For Scenario B (Broad Research), you MUST use the URLs provided in the 'Verified Search Data' to create clickable links in the References section."

    # --- 2. GENERAL WEB MODE ---
    else: 
        role_desc = "You are an articulate AI Assistant."
        
        structure = f"""
        ADAPTIVE FORMATTING INSTRUCTIONS:
        
        **SCENARIO A: Direct Question / Specific Follow-up**
        (e.g., "How does this compare to X?", "Explain the methodology", "Summarize this part")
        - Format: **Write exactly ONE single, comprehensive paragraph.**
        - Length: Target approximately **300 words**. (IGNORE user's '{length}' setting; always write ~300 words here).
        - Content: Dive straight into the answer. Do not use Intro/Conclusion headers. Flowing text only.
        
        **SCENARIO B: Broad Research Topic**
        (e.g., "The History of AI", "Global Warming Trends")
        - Format: Structured Report (Introduction, Key Findings, Conclusion).
        - Guideline: {b_length_instruction}
        """
        
        citation_instruction = "Do NOT include a 'References' section. Do NOT include links. Just write a clean narrative."

    # --- 3. FINAL PROMPT ---
    prompt = f"""
    {role_desc}
    
    User Input: {topic}
    
    {structure}
    
    {citation_instruction}
    
    CRITICAL FORMATTING RULE: Do NOT wrap the output in ```markdown or ``` code blocks. Return raw markdown text only.

    Verified Search Data:
    {data}
    """

    response = llm.invoke(prompt)
    
    # --- 4. CLEANUP (Force removal of code blocks) ---
    clean_content = response.content.replace('```markdown', '').replace('```', '').strip()
    
    return {"final_report": clean_content}