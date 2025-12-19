def writer_node(state, llm):
    topic = state['topic']
    data = state['search_results']
    # --- FIX 1: Access History ---
    history = state.get('chat_history', '') 
    
    length = state.get('summary_length', 'Detailed')
    search_mode = state.get('search_mode', 'General Web')

    # --- 0. DEFINE LENGTH INSTRUCTION ---
    if length == "Short":
        b_length_instruction = "Length Constraint: Target approx 500 words. Be concise."
    else:
        b_length_instruction = "Length Constraint: Target approx 800+ words. Provide comprehensive detail."

    # --- 1. ACADEMIC MODE ---
    if search_mode == "Academic Papers":
        role_desc = "You are an Academic Researcher."
        
        structure = f"""
        ADAPTIVE FORMATTING - ANALYZE THE INPUT CAREFULLY:
        
        **SCENARIO A: Direct Question / Specific Detail / Follow-up**
        (Triggers: "Explain...", "What is...", "Summarize the [section]...", "limitations?", "results?", "meaning of X")
        - **Format:** Write exactly **ONE single, comprehensive paragraph**.
        - **Length:** Target **300 words**.
        - **Prohibition:** NO Headers. NO Bullet Points. Just the answer.
        - **Citations:** Do NOT include references.
        
        **SCENARIO B: Broad Deep Research / Full Summary**
        (Triggers: "Summarize this paper", "Deep research on [Paper Name]", "Full analysis", or ANY NEW TOPIC)
        - **Format:** Full Academic Report with Side Headings.
        - **Guideline:** {b_length_instruction}
        - **Structure:**
          ### 📄 Title
          ### 📝 Abstract
          ### 📚 Literature Review
          ### 🔬 Methodology
          ### ⚠️ Limitations
          ### 🔗 References (STRICTLY as markdown links: - [Title](URL))
        """
        citation_instruction = "For Scenario B (Full Summary), you MUST use the URLs provided to create clickable links."

    # --- 2. GENERAL WEB MODE ---
    else: 
        role_desc = "You are an articulate AI Assistant."
        
        structure = f"""
        ADAPTIVE FORMATTING:
        
        **SCENARIO A: Direct Question / Follow-up / Summary of Previous**
        (Triggers: "Summarize previous", "Short summary", "What did you just say?", "Explain that")
        - **Format:** Write exactly **ONE single, comprehensive paragraph** (approx 300 words).
        - **Rule:** Do NOT use headers. Do NOT use bullet points.
        
        **SCENARIO B: Broad Research Topic / New Topic**
        - Format: Structured Report (Introduction, Key Findings, Conclusion).
        - Guideline: {b_length_instruction}
        """
        citation_instruction = "Do NOT include a 'References' section. Do NOT include links."

    # --- 3. FINAL PROMPT ---
    prompt = f"""
    {role_desc}
    
    PREVIOUS CONVERSATION CONTEXT:
    {history}

    CURRENT USER INPUT: {topic}
    
    {structure}
    
    {citation_instruction}

    Verified Search Data:
    {data}
    
    # ==================================================
    # 🛑 FINAL RULES
    # ==================================================
    1. **TOPIC ISOLATION:** If the User Input seems unrelated to the previous context, treat it as a brand new topic.
    2. **ANTI-REGURGITATION:** Do NOT repeat the User Input or Context at the start.
    3. **START IMMEDIATELY:** Start your response with the answer/report content.
    4. **CLEAN OUTPUT:** Do NOT wrap the output in code blocks.
    """

    response = llm.invoke(prompt)
    
    # --- 4. CLEANUP ---
    clean_content = response.content.replace('```markdown', '').replace('```', '').strip()
    
    return {"final_report": clean_content}