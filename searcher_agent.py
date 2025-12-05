def searcher_node(state, tavily_client):
    """
    Executes the search plan using Tavily.
    Args:
        state: AgentState
        tavily_client: The initialized TavilyClient
    """
    queries = state['research_plan']
    results = []

    for q in queries:
        try:
            # search_depth="basic" is faster/cheaper, "advanced" is deeper
            response = tavily_client.search(query=q, max_results=1, search_depth="basic")
            if response['results']:
                content = response['results'][0]['content']
                results.append(f"Source: {q}\nContent: {content}")
            else:
                results.append(f"Source: {q}\nContent: No data found.")
        except Exception as e:
            results.append(f"Error searching {q}: {e}")

    combined_content = "\n\n".join(results)
    return {"search_results": combined_content}