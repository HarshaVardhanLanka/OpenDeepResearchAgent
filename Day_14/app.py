import streamlit as st
from memory import HistoryManager
from utils import extract_pdf_text
from graph_builder import build_graph

# ==========================================
# 🔐 HARDCODED API KEYS
# ==========================================
OPENROUTER_API_KEY = "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"  # <--- PASTE YOUR OPENROUTER KEY HERE
TAVILY_API_KEY = "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"          # <--- PASTE YOUR TAVILY KEY HERE
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
if not st.session_state.messages:
    st.markdown("""
    <style>
    div[data-testid="stBottom"] { bottom: 50vh !important; transition: bottom 0.5s ease; padding-bottom: 0px; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    .stChatMessage {background-color: transparent;}
    .stButton button {width: 100%; text-align: left; border-radius: 5px;}
    h1 {font-size: 28px;}
    div[data-testid="stSidebar"] button:first-child {
        background-color: #FF4B4B15; 
        border: 1px solid #FF4B4B;
        color: #FF4B4B;
        text-align: center;
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
        st.success("✅ API Keys Active") # Visual confirmation
        
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

    # --- TAB 3: HISTORY ---
    with tab_history:
        st.subheader("Past Researches")
        history = memory.load_history()
        if not history:
            st.caption("No history yet.")
        else:
            for entry in reversed(history):
                time_label = entry['timestamp'].split(' ')[1]
                label = f"{time_label} - {entry['input'][:15]}..."
                
                with st.expander(label):
                    st.caption(f"Topic: {entry['input']}")
                    
                    col1, col2 = st.columns(2)
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
    # Pass the hardcoded keys to the next step logic
    if not OPENROUTER_API_KEY or not TAVILY_API_KEY:
         st.error("⚠️ API Keys are missing in app.py!")
         st.stop()
         
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Backend Execution
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    
    # Format History
    recent_history = st.session_state.messages[:-1][-4:] 
    history_str = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_history])
    
    final_topic = prompt
    mode = "Text"
    if st.session_state.pdf_context:
        final_topic = f"User Query: {prompt}\n\nReference PDF Content: {st.session_state.pdf_context[:10000]}"
        mode = "PDF"

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # PASS HARDCODED KEYS HERE
            app_graph = build_graph(OPENROUTER_API_KEY, TAVILY_API_KEY)
            
            status_placeholder = st.status("🤖 Agent Working...", expanded=False)
            status_placeholder.write("🧠 Planner: Planning strategy...")
            status_placeholder.write("🔎 Searcher: Gathering papers via Tavily...")
            status_placeholder.write(f"✍️ Writer: Drafting {search_mode}...")
            
            final_state = app_graph.invoke({
                "topic": final_topic,
                "chat_history": history_str,
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