def writer_node(state, llm):
    """
    Synthesizes the report.
    Args:
        state: AgentState
        llm: The initialized ChatGoogleGenerativeAI instance
    """
    topic = state['topic']
    data = state['search_results']

    prompt = f"""
    You are a Senior Technical Writer.

    Original Topic/Context: {topic[:500]}... 

    Verified Research Data:
    {data}

    Task: Write a professional, structured summary.
    1. Introduction
    2. Key Findings (incorporate the research data)
    3. Conclusion

    Format: Markdown.
    """

    response = llm.invoke(prompt)
    return {"final_report": response.content}