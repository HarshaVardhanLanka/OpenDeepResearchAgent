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

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* 1. Clean Chat Bubbles */
    .stChatMessage {
        background-color: transparent;
    }
    
    /* 2. Sidebar Buttons */
    .stButton button {
        width: 100%; 
        text-align: left; 
        border-radius: 20px;
    }
    
    /* 3. Header Size */
    h1 {
        font-size: 48px;
    }

    /* 4. LIFT INPUT BAR UP */
    /* This targets the bottom container and adds padding below it */
    div[data-testid="stBottom"] {
        padding-bottom: 100px; 
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
memory = HistoryManager()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""
if "tavily_api_key" not in st.session_state:
    st.session_state.tavily_api_key = ""

# --- SIDEBAR LOGIC ---
with st.sidebar:
    # TABS
    tab_settings, tab_history = st.tabs(["⚙️ Settings", "📚 History"])
    
    # TAB 1: SETTINGS
    with tab_settings:
        st.subheader("🔑 API Keys")
        st.session_state.google_api_key = st.text_input("Google Gemini Key", type="password", value=st.session_state.google_api_key)
        st.session_state.tavily_api_key = st.text_input("Tavily API Key", type="password", value=st.session_state.tavily_api_key)
        
        st.divider()
        
        st.subheader("📎 Document Upload")
        
        # Logic: Toggle between Uploader and Info Box
        if not st.session_state.pdf_name:
            uploaded_file = st.file_uploader("Upload PDF context", type=["pdf"])
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    raw_text = extract_pdf_text(uploaded_file)
                    st.session_state.pdf_context = raw_text
                    st.session_state.pdf_name = uploaded_file.name
                    st.rerun()
        else:
            st.info(f"**Current Context:**\n\n📄 {st.session_state.pdf_name}")
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

# --- MAIN CHAT INTERFACE ---
st.title("🧠 Open Deep Research Agent")
st.caption("Powered by LangGraph, Gemini & Tavily")

# Context Badge
if st.session_state.pdf_name:
    st.info(f"📎 **Active Context:** Analyzing {st.session_state.pdf_name}")

# 1. Display Messages
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 2. Chat Input
if prompt := st.chat_input("Ask a research question..."):
    
    # Check Keys
    if not st.session_state.google_api_key or not st.session_state.tavily_api_key:
        st.error("⚠️ Please set your API Keys in the Settings tab.")
        st.stop()
    
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
        
    # 3. Prepare Logic
    final_topic = prompt
    mode = "Text"
    if st.session_state.pdf_context:
        final_topic = f"User Query: {prompt}\n\nReference PDF Content: {st.session_state.pdf_context[:15000]}"
        mode = "PDF"

    # 4. Run Backend
    with st.chat_message("assistant", avatar="🤖"):
        try:
            # Build Graph
            app_graph = build_graph(st.session_state.google_api_key, st.session_state.tavily_api_key)
            
            # Visual Status
            status_placeholder = st.status("🤖 Agent Working...", expanded=True)
            
            status_placeholder.write("🧠 Planner: Analyzing request...")
            status_placeholder.write("🔎 Searcher: Verifying with Tavily...")
            status_placeholder.write("✍️ Writer: Drafting report...")
            
            # Execute
            final_state = app_graph.invoke({"topic": final_topic})
            report = final_state['final_report']
            
            status_placeholder.update(label="✅ Complete", state="complete", expanded=False)
            
            st.markdown(report)
            
            # Save Session & History
            st.session_state.messages.append({"role": "assistant", "content": report})
            memory.save_entry(prompt, mode, report)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")