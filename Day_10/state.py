from typing import TypedDict, List

class AgentState(TypedDict):
    topic: str                
    summary_length: str       # <--- NEW FIELD
    research_plan: List[str]  
    search_results: str       
    final_report: str         