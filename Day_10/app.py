import streamlit as st
from memory import HistoryManager
from utils import extract_pdf_text
from graph_builder import build_graph

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Open Deep Research Agent",
    page_icon="🧠",
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
    
# CHANGED: Initialize OpenRouter Key instead of Google
if "openrouter_api_key" not in st.session_state:
    st.session_state.openrouter_api_key = ""
if "tavily_api_key" not in st.session_state:
    st.session_state.tavily_api_key = ""

# --- CONDITIONAL CSS (Center Input) ---
if not st.session_state.messages:
    st.markdown("""
    <style>
    div[data-testid="stBottom"] {
        bottom: 50vh !important;
        transition: bottom 0.5s ease;
        padding-bottom: 0px;
    }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- GENERAL CSS ---
st.markdown("""
<style>
    .stChatMessage {background-color: transparent;}
    .stButton button {width: 100%; text-align: left; border-radius: 5px;}
    h1 {font-size: 28px;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    tab_settings, tab_history = st.tabs(["⚙️ Settings", "📚 History"])
    
    # TAB 1: SETTINGS
    with tab_settings:
        st.subheader("🔑 API Keys")
        
        # CHANGED: Input for OpenRouter
        st.session_state.openrouter_api_key = st.text_input(
            "OpenRouter API Key", 
            type="password", 
            value=st.session_state.openrouter_api_key,
            help="Get key from openrouter.ai"
        )
        
        st.session_state.tavily_api_key = st.text_input(
            "Tavily API Key", 
            type="password", 
            value=st.session_state.tavily_api_key
        )
        
        st.divider()

        # REPORT LENGTH SELECTION
        st.subheader("📝 Report Style")
        report_type = st.radio(
            "Select Output Length:",
            ["Detailed Report", "Short Summary"],
            index=0
        )
        length_map = {"Detailed Report": "Detailed", "Short Summary": "Short"}
        selected_length = length_map[report_type]

        st.divider()
        
        # PDF UPLOAD LOGIC
        st.subheader("📎 Document Upload")
        if not st.session_state.pdf_name:
            uploaded_file = st.file_uploader("Upload PDF context", type=["pdf"])
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    raw_text = extract_pdf_text(uploaded_file)
                    st.session_state.pdf_context = raw_text
                    st.session_state.pdf_name = uploaded_file.name
                    st.rerun()
        else:
            st.info(f"**Context:** 📄 {st.session_state.pdf_name}")
            if st.button("❌ Remove / Upload New", type="primary"):
                st.session_state.pdf_context = ""
                st.session_state.pdf_name = None
                st.rerun()

    # TAB 2: HISTORY
    with tab_history:
        st.subheader("Past Researches")
        history = memory.load_history()
        if not history:
            st.caption("No history yet.")
        else:
            for entry in reversed(history):
                time_label = entry['timestamp'].split(' ')[1]
                label = f"{time_label} - {entry['input'][:15]}..."
                if st.button(label, key=f"hist_{entry['id']}"):
                    @st.dialog("📜 Research Report")
                    def show_report():
                        st.subheader(entry['input'])
                        st.caption(f"Date: {entry['timestamp']} | Mode: {entry['mode']}")
                        st.divider()
                        st.markdown(entry['report'])
                    show_report()

# --- MAIN CHAT ---
if not st.session_state.messages:
    st.title("🧠 Open Deep Research Agent")
    st.markdown("### What would you like to research today?")
else:
    st.caption("🧠 Open Deep Research Agent | Powered by LangGraph, OpenRouter & Tavily")
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
    # CHANGED: Check OpenRouter Key
    if not st.session_state.openrouter_api_key or not st.session_state.tavily_api_key:
        st.error("⚠️ Please set your OpenRouter & Tavily Keys in the Settings tab.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Backend Execution
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    
    final_topic = prompt
    mode = "Text"
    if st.session_state.pdf_context:
        # Keep context reasonable to avoid OpenRouter limits
        final_topic = f"User Query: {prompt}\n\nReference PDF Content: {st.session_state.pdf_context[:10000]}"
        mode = "PDF"

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # CHANGED: Pass OpenRouter Key
            app_graph = build_graph(st.session_state.openrouter_api_key, st.session_state.tavily_api_key)
            
            status_placeholder = st.status("🤖 Agent Working...", expanded=True)
            status_placeholder.write("🧠 Planner: Analyzing request...")
            status_placeholder.write("🔎 Searcher: Verifying with Tavily...")
            status_placeholder.write(f"✍️ Writer: Drafting {selected_length} report...")
            
            final_state = app_graph.invoke({
                "topic": final_topic,
                "summary_length": selected_length
            })
            
            report = final_state['final_report']
            status_placeholder.update(label="✅ Complete", state="complete", expanded=False)
            st.markdown(report)
            
            st.session_state.messages.append({"role": "assistant", "content": report})
            memory.save_entry(prompt, mode, report)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")