import os
import json
import datetime

class HistoryManager:
    def __init__(self):
        self.history_file = "agent_history.json"

    def load_history(self):
        """Loads history from a JSON file if it exists."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    # UPDATED FUNCTION SIGNATURE
    def save_entry(self, input_text, mode, final_report, messages):
        """Saves a new research session to memory."""
        history = self.load_history()
        entry = {
            "id": len(history) + 1,
            "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            "mode": mode,
            "input": input_text,
            "report": final_report,
            "chat_history": messages  # <--- Now we save the full chat history
        }
        history.append(entry)
        with open(self.history_file, 'w') as f:
            json.dump(history, f)
        return entry