from typing import TypedDict, List

class AgentState(TypedDict):
    topic: str                
    summary_length: str       
    search_mode: str          # <--- NEW FIELD (General vs Academic)
    research_plan: List[str]  
    search_results: str       
    final_report: str         