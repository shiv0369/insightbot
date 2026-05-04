import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Import our previous building blocks
from text_to_sql import generate_sql, is_safe_query, execute_sql, get_schema
from chart_generator import generate_chart
from rag_engine import search_relevant_context


# ============================================================
# SETUP
# ============================================================
load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,  # tiny bit of warmth for explanations
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# The "Final Answer" prompt — combines numbers + context
# ============================================================
ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are InsightBot, a friendly and expert data analyst.
Your job is to answer business questions using TWO sources:
1. SQL query results (the numbers)
2. Business report excerpts (the context / "why")

RULES:
- Start with the key numbers from the SQL result.
- Then explain the "why" using the report context, citing the report name.
- Be concise: 3-5 sentences total.
- If the report context isn't relevant to the question, just summarize the numbers.
- Never make up numbers or facts not in the data.
"""),
    ("user", """QUESTION: {question}

SQL RESULT:
{sql_result}

RELEVANT REPORT EXCERPTS:
{report_context}

Write a complete, helpful answer:""")
])


# ============================================================
# THE FULL PIPELINE
# ============================================================
def ask_insightbot(question: str, show_chart: bool = True):
    """
    Full InsightBot pipeline:
    Question → SQL → Result → RAG → LLM Explanation → Chart
    """
    print(f"\n{'='*65}")
    print(f"❓ {question}")
    print(f"{'='*65}\n")
    
    # ===== Stage 1: SQL =====
    print("🤖 [1/4] Generating SQL...")
    schema = get_schema()
    sql = generate_sql(question, schema)
    print(f"   SQL: {sql}\n")
    
    if not is_safe_query(sql):
        print("🚫 Unsafe query blocked.")
        return
    
    # ===== Stage 2: Execute SQL =====
    print("📊 [2/4] Running query...")
    try:
        result_df = execute_sql(sql)
        print(f"   {len(result_df)} rows returned.\n")
    except Exception as e:
        print(f"❌ SQL error: {e}")
        return
    
    # ===== Stage 3: RAG search for context =====
    print("📚 [3/4] Searching PDF reports for context...")
    relevant_chunks = search_relevant_context(question, top_k=3)
    report_context = "\n\n".join(
        f"[From {c['source']}]: {c['text']}" for c in relevant_chunks
    )
    print(f"   Found {len(relevant_chunks)} relevant excerpts.\n")
    
    # ===== Stage 4: LLM combines numbers + context =====
    print("✍️  [4/4] Generating final answer...")
    sql_result_text = result_df.to_string(index=False)
    
    chain = ANSWER_PROMPT | llm
    response = chain.invoke({
        "question": question,
        "sql_result": sql_result_text,
        "report_context": report_context
    })
    
    print("\n" + "─"*65)
    print("💡 INSIGHTBOT ANSWER:")
    print("─"*65)
    print(response.content)
    print("─"*65)
    
    # ===== Bonus: Chart =====
    if show_chart and not result_df.empty:
        fig = generate_chart(result_df, question)
        if fig:
            fig.write_html("latest_chart.html", auto_open=True)
            print("\n🎨 Chart opened in browser.")


# ============================================================
# INTERACTIVE MODE
# ============================================================
if __name__ == "__main__":
    
    print("\n" + "="*65)
    print("🤖 InsightBot — Your AI Data Analyst")
    print("="*65)
    print("Ask questions in plain English. Type 'quit' to exit.\n")
    
    while True:
        question = input("\nYou: ").strip()
        
        if question.lower() in ["quit", "exit", "q"]:
            print("\n👋 Goodbye!")
            break
        
        if not question:
            continue
        
        try:
            ask_insightbot(question)
        except Exception as e:
            print(f"\n❌ Something went wrong: {e}")