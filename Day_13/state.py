from typing import TypedDict, List

class AgentState(TypedDict):
    topic: str                
    chat_history: str         # <--- NEW FIELD (Previous conversation)
    summary_length: str       
    search_mode: str          
    research_plan: List[str]  
    search_results: str       
    final_report: str         