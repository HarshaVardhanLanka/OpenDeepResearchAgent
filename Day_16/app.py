import streamlit as st
from datetime import datetime  # <--- Added for date formatting
from memory import HistoryManager
from utils import extract_pdf_text
from graph_builder import build_graph

# ==========================================
# 🔐 SECURE API KEY HANDLING
# ==========================================
# Try loading from local config first, otherwise check Cloud Secrets
try:
    from config import OPENROUTER_API_KEY, TAVILY_API_KEY
except ImportError:
    # This runs when deployed on Streamlit Cloud
    if "OPENROUTER_API_KEY" in st.secrets and "TAVILY_API_KEY" in st.secrets:
        OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
        TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    else:
        st.error("🚨 API Keys not found! Please set them in Streamlit Secrets.")
        st.stop()
# ==========================================

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Open Deep Research Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZATION ---
memory = HistoryManager()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# --- CSS STYLING ---
# 1. Center Input if Chat is Empty
if not st.session_state.messages:
    st.markdown("""
    <style>
    div[data-testid="stBottom"] { bottom: 50vh !important; transition: bottom 0.5s ease; padding-bottom: 0px; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. General UI Polish
st.markdown("""
<style>
    .stChatMessage {background-color: transparent;}
    .stButton button {width: 100%; border-radius: 5px;}
    h1 {font-size: 28px;}
    
    /* Highlight New Chat Button */
    div[data-testid="stSidebar"] button:first-child {
        background-color: #FF4B4B15; 
        border: 1px solid #FF4B4B;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    
    # NEW CHAT BUTTON
    if st.button("➕ Start New Chat"):
        st.session_state.messages = []
        st.session_state.pdf_context = ""
        st.session_state.pdf_name = None
        st.rerun()

    # TABS
    tab_settings, tab_upload, tab_history = st.tabs(["⚙️ Settings", "📎 Upload", "📚 History"])
    
    # --- TAB 1: SETTINGS ---
    with tab_settings:
        if OPENROUTER_API_KEY and TAVILY_API_KEY:
            st.success("✅ API Keys Loaded")
        else:
            st.error("❌ Keys missing in config.py")
            
        st.divider()

        st.subheader("🔍 Search Focus")
        search_mode = st.radio("Target:", ["General Web", "Academic Papers"], index=0)
        
        st.divider()

        st.subheader("📝 Output Length")
        report_type = st.radio("Detail Level:", ["Detailed Report", "Short Summary"], index=0)
        length_map = {"Detailed Report": "Detailed", "Short Summary": "Short"}
        selected_length = length_map[report_type]

    # --- TAB 2: PDF UPLOAD ---
    with tab_upload:
        st.subheader("📄 Document Context")
        
        if not st.session_state.pdf_name:
            st.markdown("Upload a research paper to analyze it alongside web search.")
            uploaded_file = st.file_uploader("Choose PDF", type=["pdf"])
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    raw_text = extract_pdf_text(uploaded_file)
                    st.session_state.pdf_context = raw_text
                    st.session_state.pdf_name = uploaded_file.name
                    st.rerun()
        else:
            st.success(f"**Active File:**\n{st.session_state.pdf_name}")
            st.markdown("The agent will now prioritize this document in its research.")
            
            if st.button("❌ Remove PDF", type="primary"):
                st.session_state.pdf_context = ""
                st.session_state.pdf_name = None
                st.rerun()

        # --- TAB 3: HISTORY (Modified for Smart Date/Time) ---
    with tab_history:
        st.subheader("Past Researches")
        history = memory.load_history()
        if not history:
            st.caption("No history yet.")
        else:
            for entry in reversed(history):
                # --- SMART DATE LOGIC ---
                try:
                    # 1. Parse the stored timestamp string
                    dt_obj = datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M")
                    
                    # 2. Get current date
                    now = datetime.now()
                    
                    # 3. Compare dates
                    if dt_obj.date() == now.date():
                        # If TODAY: Show 12-hour time (e.g., "02:30 PM")
                        time_label = dt_obj.strftime("%I:%M %p")
                    else:
                        # If OLDER: Show Date (e.g., "27 Oct 2023")
                        time_label = dt_obj.strftime("%d %b %Y")
                        
                except Exception:
                    # Fallback if format is wrong
                    time_label = entry['timestamp']

                # Create the label
                short_input = entry['input'][:18] + "..." if len(entry['input']) > 18 else entry['input']
                label = f"{time_label} - {short_input}"
                
                # --- EXPANDER LAYOUT (Same as before) ---
                with st.expander(label):
                    st.caption(f"**Full Topic:** {entry['input']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("👁️ View", key=f"view_{entry['id']}"):
                            @st.dialog("📜 Research Report")
                            def show_report():
                                st.subheader(entry['input'])
                                st.markdown(entry['report'])
                            show_report()
                            
                    with col2:
                        if st.button("🔄 Resume", key=f"load_{entry['id']}"):
                            saved_history = entry.get('chat_history', None)
                            if saved_history:
                                st.session_state.messages = saved_history
                            else:
                                st.session_state.messages = [
                                    {"role": "user", "content": entry['input']},
                                    {"role": "assistant", "content": entry['report']}
                                ]
                            st.success("Chat Loaded!")
                            st.rerun()
                            
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_{entry['id']}"):
                            memory.delete_entry(entry['id'])
                            st.rerun()

# --- MAIN CHAT ---
if not st.session_state.messages:
    st.title("🤖 Open Deep Research Agent")
    st.markdown("### What would you like to research today?")
else:
    st.caption("🤖 Open Deep Research Agent | Powered by LangGraph, OpenRouter & Tavily")
    if st.session_state.pdf_name:
        st.info(f"📎 **Active Context:** {st.session_state.pdf_name}")

# Display Messages
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat Input
placeholder = "Ask a research question..." if st.session_state.messages else "Enter a topic..."

if prompt := st.chat_input(placeholder):
    if not OPENROUTER_API_KEY or not TAVILY_API_KEY:
         st.error("⚠️ API Keys are missing in config.py!")
         st.stop()
         
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Backend Execution
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    
    # --- BALANCED HISTORY STRATEGY ---
    recent_messages = st.session_state.messages[:-1] 
    formatted_history = []
    
    for i, msg in enumerate(reversed(recent_messages)):
        role = msg['role'].upper()
        content = msg['content']
        if i > 2 and len(content) > 500:
             content = content[:200] + "... [Old Context Truncated]"
        formatted_history.insert(0, f"{role}: {content}")

    final_history_str = "\n".join(formatted_history[-10:])
    
    final_topic = prompt
    mode = "Text"
    if st.session_state.pdf_context:
        pdf_limit = 100000 
        final_topic = f"User Query: {prompt}\n\nReference PDF Content: {st.session_state.pdf_context[:pdf_limit]}"
        mode = "PDF"

    with st.chat_message("assistant", avatar="🤖"):
        try:
            app_graph = build_graph(OPENROUTER_API_KEY, TAVILY_API_KEY)
            
            # Status Indicator
            status_placeholder = st.status("🤖 Agent Working...", expanded=False)
            status_placeholder.write("🧠 Planner: Planning strategy...")
            status_placeholder.write("🔎 Searcher: Gathering papers via Tavily...")
            status_placeholder.write(f"✍️ Writer: Drafting {search_mode}...")
            
            final_state = app_graph.invoke({
                "topic": final_topic,
                "chat_history": final_history_str, 
                "summary_length": selected_length,
                "search_mode": search_mode 
            })
            
            report = final_state['final_report']
            status_placeholder.update(label="✅ Complete", state="complete", expanded=False)
            
            st.markdown(report)
            
            st.session_state.messages.append({"role": "assistant", "content": report})
            memory.save_entry(prompt, mode, report, st.session_state.messages)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")