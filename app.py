import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Import all our building blocks from previous days
from text_to_sql import generate_sql, is_safe_query, execute_sql, get_schema
from chart_generator import generate_chart
from rag_engine import search_relevant_context

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


# ============================================================
# PAGE CONFIGURATION (must be first Streamlit command)
# ============================================================
st.set_page_config(
    page_title="InsightBot — AI Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CACHED RESOURCES (load once, reuse across reruns)
# ============================================================
@st.cache_resource
def load_llm():
    """Load the LLM only once — cached for speed."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY")
    )

@st.cache_data
def load_schema():
    """Cache the schema so we don't re-fetch every interaction."""
    return get_schema()


llm = load_llm()
schema = load_schema()


# ============================================================
# THE ANSWER PROMPT (same as insightbot.py)
# ============================================================
ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are InsightBot, a friendly and expert data analyst.
You answer questions using TWO sources:
1. SQL query results (the real, current numbers — ALWAYS TRUST THESE)
2. Business report excerpts (context about WHY things happened)

CRITICAL RULES:
- The SQL result is the source of truth for ALL numbers. Quote it exactly.
- If the SQL result has data, you MUST start by stating those numbers.
- If the SQL result is empty or shows "unavailable", say "I couldn't retrieve the data" — do NOT invent numbers from reports.
- Use report excerpts ONLY to explain "why" something happened.
- Keep answer to 3-5 sentences. Cite the report by filename when used.
"""),
    ("user", """QUESTION: {question}

SQL RESULT:
{sql_result}

RELEVANT REPORT EXCERPTS:
{report_context}

Now write a clear, accurate answer:""")
])


# ============================================================
# MAIN PROCESSING FUNCTION
# ============================================================
def process_question(question: str):
    """
    Run the full pipeline and return all outputs as a dict.
    """
    result = {
        "question": question,
        "sql": None,
        "data": None,
        "chart": None,
        "answer": None,
        "sources": [],
        "error": None
    }
    
    try:
        # Stage 1: Generate SQL
        sql = generate_sql(question, schema)
        result["sql"] = sql
        
        # Safety check
        if not is_safe_query(sql):
            result["error"] = "Query blocked for safety reasons."
            return result
        
        # Stage 2: Execute SQL
        data = execute_sql(sql)
        result["data"] = data
        
        # Stage 3: Generate chart
        if not data.empty:
            result["chart"] = generate_chart(data, question)
        
        # Stage 4: RAG search
        chunks = search_relevant_context(question, top_k=3)
        result["sources"] = chunks
        report_context = "\n\n".join(
            f"[From {c['source']}]: {c['text']}" for c in chunks
        )
        
        # Stage 5: Final answer
        sql_result_text = data.to_string(index=False) if not data.empty else "No data returned"
        chain = ANSWER_PROMPT | llm
        response = chain.invoke({
            "question": question,
            "sql_result": sql_result_text,
            "report_context": report_context
        })
        result["answer"] = response.content
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


# ============================================================
# SIDEBAR — Project info and example questions
# ============================================================
with st.sidebar:
    st.title("🤖 InsightBot")
    st.markdown("**Your AI Data Analyst**")
    st.markdown("---")
    
    st.markdown("### 💡 What I Can Do")
    st.markdown("""
    - 📊 Convert your English questions into SQL
    - 📈 Generate interactive charts automatically
    - 📚 Explain "why" using business reports
    - 💬 Remember our conversation
    """)
    
    st.markdown("---")
    st.markdown("### ✨ Try These Questions")
    
    example_questions = [
        "What were total sales by region?",
        "Top 5 products by revenue",
        "Why did East region sales drop in Q3?",
        "Show monthly sales trend in 2017",
        "Which sub-categories are losing money?",
        "Who are the top 10 customers by profit?",
    ]
    
    for q in example_questions:
        if st.button(q, key=f"ex_{q}", use_container_width=True):
            st.session_state.pending_question = q
    
    st.markdown("---")
    st.markdown("### 🛠️ Tech Stack")
    st.caption("LangChain · Groq Llama-3 · ChromaDB · SQLite · Plotly · Streamlit")
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# MAIN AREA — Header
# ============================================================
st.title("🤖 InsightBot — Conversational AI Data Analyst")
st.caption("Ask business questions in plain English. Get SQL, charts, and explanations grounded in your reports.")


# ============================================================
# CHAT HISTORY (persisted in session_state)
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            # Assistant message — show the full breakdown
            data = msg["content"]
            
            if data.get("error"):
                st.error(f"❌ {data['error']}")
            else:
                # Main answer
                st.markdown("### 💡 Answer")
                st.markdown(data["answer"])
                
                # Tabs for details (keeps UI clean)
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "📋 Data", "🔧 SQL", "📚 Sources"])
                
                with tab1:
                    if data.get("chart"):
                        st.plotly_chart(data["chart"], use_container_width=True, key=f"chart_{id(data)}")
                    else:
                        st.info("No chart available for this result.")
                
                with tab2:
                    if data.get("data") is not None and not data["data"].empty:
                        st.dataframe(data["data"], use_container_width=True)
                        # CSV download button
                        csv = data["data"].to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇️ Download CSV",
                            csv,
                            "insightbot_result.csv",
                            "text/csv",
                            key=f"dl_{id(data)}"
                        )
                    else:
                        st.info("No data returned.")
                
                with tab3:
                    st.code(data["sql"], language="sql")
                
                with tab4:
                    if data.get("sources"):
                        for i, src in enumerate(data["sources"], 1):
                            with st.expander(f"📄 {src['source']} (relevance: {1 - src['distance']:.2%})"):
                                st.markdown(src["text"])
                    else:
                        st.info("No sources cited.")


# ============================================================
# CHAT INPUT
# ============================================================
user_input = st.chat_input("Ask me anything about your business data...")

# Handle question from sidebar example button
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None


# ============================================================
# PROCESS NEW QUESTION
# ============================================================
if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Process and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking... (generating SQL, querying data, searching reports)"):
            result = process_question(user_input)
        
        if result.get("error"):
            st.error(f"❌ {result['error']}")
        else:
            st.markdown("### 💡 Answer")
            st.markdown(result["answer"])
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "📋 Data", "🔧 SQL", "📚 Sources"])
            
            with tab1:
                if result.get("chart"):
                    st.plotly_chart(result["chart"], use_container_width=True, key=f"new_chart_{len(st.session_state.messages)}")
                else:
                    st.info("No chart available.")
            
            with tab2:
                if result.get("data") is not None and not result["data"].empty:
                    st.dataframe(result["data"], use_container_width=True)
                    csv = result["data"].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download CSV",
                        csv,
                        "insightbot_result.csv",
                        "text/csv",
                        key=f"new_dl_{len(st.session_state.messages)}"
                    )
                else:
                    st.info("No data returned.")
            
            with tab3:
                st.code(result["sql"], language="sql")
            
            with tab4:
                if result.get("sources"):
                    for src in result["sources"]:
                        with st.expander(f"📄 {src['source']} (relevance: {1 - src['distance']:.2%})"):
                            st.markdown(src["text"])
                else:
                    st.info("No sources cited.")
    
    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": result})