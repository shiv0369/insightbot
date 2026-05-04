import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from chart_generator import generate_chart

# ============================================================
# SETUP
# ============================================================
load_dotenv()

DB_PATH = "data/superstore.db"

# Initialize the LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# STEP 1: Get the database schema
# ============================================================
def get_schema():
    """Returns a clean text description of the database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(sales);")
    columns = cursor.fetchall()
    
    # Build a clean schema description for the LLM
    schema = "Table: sales\nColumns:\n"
    for col in columns:
        schema += f"  - {col[1]} ({col[2]})\n"
    
    # Add 2 sample rows to help the LLM understand the data format
    cursor.execute("SELECT * FROM sales LIMIT 2")
    samples = cursor.fetchall()
    schema += f"\nSample rows: {samples}"
    
    conn.close()
    return schema


# ============================================================
# STEP 2: Build the prompt template
# This is the MOST IMPORTANT part — it teaches the LLM how to behave
# ============================================================
SQL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert SQL analyst working with a SQLite database.
Your job is to convert natural-language business questions into SQL queries.

DATABASE SCHEMA:
{schema}

RULES (very important):
1. Generate ONLY a valid SQLite SQL query. No explanations, no markdown, no ```sql fences.
2. Use only the columns and table that exist in the schema above.
3. Always use lowercase column names exactly as shown in the schema.
4. For date filtering, use SQLite functions like strftime('%Y', order_date) = '2017'.
5. When asked for "top N", use ORDER BY ... DESC LIMIT N.
6. Round monetary values to 2 decimals using ROUND(column, 2).
7. Never write INSERT, UPDATE, DELETE, DROP, or ALTER queries — only SELECT.
8. If the question is unclear or impossible to answer with this schema, return: SELECT 'Cannot answer this question' AS error;

EXAMPLES:

Question: What were the top 3 products by sales?
SQL: SELECT product_name, ROUND(SUM(sales), 2) AS total_sales FROM sales GROUP BY product_name ORDER BY total_sales DESC LIMIT 3;

Question: Which region had the highest profit in 2017?
SQL: SELECT region, ROUND(SUM(profit), 2) AS total_profit FROM sales WHERE strftime('%Y', order_date) = '2017' GROUP BY region ORDER BY total_profit DESC LIMIT 1;

Question: How many orders did each customer place?
SQL: SELECT customer_name, COUNT(DISTINCT order_id) AS order_count FROM sales GROUP BY customer_name ORDER BY order_count DESC;
"""),
    ("user", "Question: {question}\nSQL:")
])


# ============================================================
# STEP 3: Generate SQL from a natural-language question
# ============================================================
def generate_sql(question: str, schema: str) -> str:
    """Sends the question + schema to the LLM and returns a SQL query."""
    
    # Build the prompt and send to LLM
    chain = SQL_PROMPT | llm
    response = chain.invoke({"schema": schema, "question": question})
    
    sql = response.content.strip()
    
    # Clean up: remove any accidental markdown fences
    sql = sql.replace("```sql", "").replace("```", "").strip()
    
    return sql


# ============================================================
# STEP 4: Safety check — make sure it's only a SELECT query
# ============================================================
def is_safe_query(sql: str) -> bool:
    """Block any query that isn't a SELECT (no DELETE, DROP, etc.)."""
    sql_upper = sql.upper().strip()
    
    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False
    
    # Block dangerous keywords
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    for word in forbidden:
        if word in sql_upper:
            return False
    
    return True


# ============================================================
# STEP 5: Execute the SQL on the database
# ============================================================
def execute_sql(sql: str) -> pd.DataFrame:
    """Runs the SQL query and returns the result as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        result = pd.read_sql_query(sql, conn)
        return result
    finally:
        conn.close()


# ============================================================
# STEP 6: The full pipeline — tie it all together
# ============================================================
def ask_question(question: str, show_chart: bool = True):
    """Main pipeline: English → SQL → Result → Chart."""
    print(f"\n{'='*65}")
    print(f"❓ Question: {question}")
    print(f"{'='*65}")
    
    schema = get_schema()
    
    print("🤖 Generating SQL...")
    sql = generate_sql(question, schema)
    print(f"📝 SQL Generated:\n{sql}\n")
    
    if not is_safe_query(sql):
        print("🚫 Unsafe query blocked.")
        return None, None
    
    try:
        result = execute_sql(sql)
        print(f"📊 Result ({len(result)} rows):")
        print(result.to_string(index=False))
        
        # NEW: Generate and show chart
        if show_chart and not result.empty:
            print("\n🎨 Generating chart...")
            fig = generate_chart(result, question)
            if fig:
                fig.write_html("latest_chart.html", auto_open=True)
                print("   Chart opened in browser.")
        
        return sql, result
    except Exception as e:
        print(f"❌ Error: {e}")
        return sql, None

# ============================================================
# RUN IT
# ============================================================
if __name__ == "__main__":
    
    print("\n" + "="*65)
    print("🤖 InsightBot — Ask me anything about the Superstore data!")
    print("="*65)
    print("Type 'quit' to exit.\n")
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() in ["quit", "exit", "q"]:
            print("👋 Bye!")
            break
        
        if not question:
            continue
        
        ask_question(question)
        print()

