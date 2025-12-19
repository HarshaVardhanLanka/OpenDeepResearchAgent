def searcher_node(state, tavily_client):
    """
    Executes the search plan and extracts Titles and URLs for citations.
    """
    queries = state['research_plan']
    results = []

    for q in queries:
        try:
            # We fetch a bit more context to ensure we get good summaries
            response = tavily_client.search(query=q, max_results=2, search_depth="basic")
            
            for r in response.get('results', []):
                title = r.get('title', 'Unknown Source')
                url = r.get('url', '#')
                content = r.get('content', '')
                
                # Format specifically so the Writer sees the URL
                results.append(f"Title: {title}\nURL: {url}\nContent: {content}\n---")
                
        except Exception as e:
            results.append(f"Error searching {q}: {e}")

    combined_content = "\n".join(results)
    return {"search_results": combined_content}