import wikipedia

def wikipedia_search_tool(query: str) -> str:
    """Searches Wikipedia."""
    try:
        return wikipedia.summary(query, sentences=3)
    except Exception as e:
        return f"[Mock Wikipedia Result] Summary for {query} (Error: {e})"
