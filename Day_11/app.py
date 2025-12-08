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
if "openrouter_api_key" not in st.session_state:
    st.session_state.openrouter_api_key = ""
if "tavily_api_key" not in st.session_state:
    st.session_state.tavily_api_key = ""

# --- CSS ---
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
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    tab_settings, tab_history = st.tabs(["⚙️ Settings", "📚 History"])
    
    with tab_settings:
        st.subheader("🔑 API Keys")
        st.session_state.openrouter_api_key = st.text_input("OpenRouter Key", type="password", value=st.session_state.openrouter_api_key)
        st.session_state.tavily_api_key = st.text_input("Tavily API Key", type="password", value=st.session_state.tavily_api_key)
        
        st.divider()

        # --- 1. SEARCH MODE SELECTOR (NEW) ---
        st.subheader("🔍 Search Focus")
        search_mode = st.radio(
            "Target:",
            ["General Web", "Academic Papers"],
            index=0,
            help="General: Blogs, News, Wikis. Academic: Arxiv, Journals, PDF Reports."
        )
        
        st.divider()

        # --- 2. REPORT LENGTH SELECTOR ---
        st.subheader("📝 Output Length")
        report_type = st.radio(
            "Detail Level:",
            ["Detailed Report", "Short Summary"],
            index=0
        )
        length_map = {"Detailed Report": "Detailed", "Short Summary": "Short"}
        selected_length = length_map[report_type]

        st.divider()
        
        # --- 3. PDF UPLOAD ---
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

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

placeholder = "Ask a research question..." if st.session_state.messages else "Enter a topic..."

if prompt := st.chat_input(placeholder):
    if not st.session_state.openrouter_api_key or not st.session_state.tavily_api_key:
        st.error("⚠️ Please set your Keys in the Settings tab.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Backend Execution
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    
    final_topic = prompt
    mode = "Text"
    if st.session_state.pdf_context:
        final_topic = f"User Query: {prompt}\n\nReference PDF Content: {st.session_state.pdf_context[:10000]}"
        mode = "PDF"

    with st.chat_message("assistant", avatar="🤖"):
        try:
            app_graph = build_graph(st.session_state.openrouter_api_key, st.session_state.tavily_api_key)
            
            status_placeholder = st.status("🤖 Agent Working...", expanded=True)
            status_placeholder.write("🧠 Planner: Planning strategy...")
            status_placeholder.write("🔎 Searcher: Gathering papers via Tavily...")
            status_placeholder.write(f"✍️ Writer: Drafting {search_mode}...")
            
            # --- PASS BOTH MODES HERE ---
            final_state = app_graph.invoke({
                "topic": final_topic,
                "summary_length": selected_length,
                "search_mode": search_mode # <--- Passing the "Academic Papers" choice
            })
            
            report = final_state['final_report']
            status_placeholder.update(label="✅ Complete", state="complete", expanded=False)
            st.markdown(report)
            
            st.session_state.messages.append({"role": "assistant", "content": report})
            memory.save_entry(prompt, mode, report)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")