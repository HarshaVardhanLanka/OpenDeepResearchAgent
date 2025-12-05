# basic_bot.py
import re
import random

# List of (pattern, responses) pairs
RULES = [
    (re.compile(r"\b(hi|hello|hey|yo|sup)\b", re.I),
     ["Hi!", "Hello!", "Hey there!", "Yo!"]),
    (re.compile(r"\bgood (morning|afternoon|evening)\b", re.I),
     ["Good {0}!".format, "Hope your {0} is going well!".format]),
    (re.compile(r"\bhow (are|r) (you|u)\b", re.I),
     ["I'm doing great—thanks! How can I help?",
      "All good here. What's up?",
      "Pretty good! What can I do for you?"]),
    (re.compile(r"\b(thanks|thank you|thx|ty)\b", re.I),
     ["You're welcome!", "No problem!", "Anytime!"]),
    (re.compile(r"\b(bye|goodbye|see (ya|you)|later)\b", re.I),
     ["Bye!", "See you later!", "Take care!"]),
    (re.compile(r"\bhelp\b|\bwhat can you do\b", re.I),
     ["I can respond to greetings, 'how are you', 'thanks', and 'bye'."]),
    (re.compile(r"\b(what('?s| is) your name)\b", re.I),
     ["I'm BasicBot. Nice to meet you!"]),
    (re.compile(r"\bjoke\b", re.I),
     ["Why did the developer go broke? Because he used all his cache.",
      "I told a UDP joke—I'm not sure if anyone got it.",
      "There are 10 kinds of people: those who understand binary and those who don't."]),
]

def respond(text: str) -> str:
    for pattern, replies in RULES:
        m = pattern.search(text)
        if m:
            # If a reply is a formatter (for "good morning/afternoon/evening"), fill it
            candidate = random.choice(replies)
            if callable(candidate) and m.groups():
                return candidate(m.group(1).lower())
            return candidate
    return "I'm a simple bot. Try 'hi', 'how are you', 'thanks', or 'bye'."

def chat():
    print("BasicBot ready. Type 'quit' to exit.")
    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user.lower() in {"quit", "exit", "q"}:
            print("Bot: Bye!")
            break
        print("Bot:", respond(user))

if __name__ == "__main__":
    chat()