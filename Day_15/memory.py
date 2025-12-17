import os
import json
import datetime
import uuid  # <--- NEW IMPORT

class HistoryManager:
    def __init__(self):
        self.history_file = "agent_history.json"

    def load_history(self):
        """Loads history from a JSON file if it exists."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_entry(self, input_text, mode, final_report, messages):
        """Saves a new research session to memory."""
        history = self.load_history()
        
        # --- FIX: Use UUID for unique IDs instead of length ---
        entry = {
            "id": str(uuid.uuid4()), 
            "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            "mode": mode,
            "input": input_text,
            "report": final_report,
            "chat_history": messages
        }
        history.append(entry)
        with open(self.history_file, 'w') as f:
            json.dump(history, f)
        return entry

    def delete_entry(self, entry_id):
        """Deletes a specific entry by ID."""
        history = self.load_history()
        # Filter out the item with the matching ID
        new_history = [item for item in history if item['id'] != entry_id]
        
        with open(self.history_file, 'w') as f:
            json.dump(new_history, f)
        return new_history