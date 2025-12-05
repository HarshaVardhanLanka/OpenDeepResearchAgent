from typing import TypedDict, List

class AgentState(TypedDict):
    topic: str                # The User's input
    research_plan: List[str]  # Output from Planner
    search_results: str       # Output from Searcher
    final_report: str         # Output from Writer