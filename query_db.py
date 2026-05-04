import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("data/superstore.db")

# ============================================================
# Helper function: run a query and print it nicely
# ============================================================
def run_query(title, sql):
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    print(f"SQL: {sql}\n")
    result = pd.read_sql_query(sql, conn)
    print(result)

# ============================================================
# Query 1: What tables and columns are in our database?
# ============================================================
run_query(
    "What columns does the 'sales' table have?",
    "PRAGMA table_info(sales);"
)

# ============================================================
# Query 2: Total sales by region
# ============================================================
run_query(
    "Total sales by region",
    """
    SELECT region, ROUND(SUM(sales), 2) AS total_sales
    FROM sales
    GROUP BY region
    ORDER BY total_sales DESC;
    """
)

# ============================================================
# Query 3: Top 5 products by revenue
# ============================================================
run_query(
    "Top 5 products by revenue",
    """
    SELECT product_name, ROUND(SUM(sales), 2) AS revenue
    FROM sales
    GROUP BY product_name
    ORDER BY revenue DESC
    LIMIT 5;
    """
)

# ============================================================
# Query 4: Profit by category and sub-category
# ============================================================
run_query(
    "Profit by category and sub-category",
    """
    SELECT category, sub_category,
           ROUND(SUM(profit), 2) AS total_profit
    FROM sales
    GROUP BY category, sub_category
    ORDER BY total_profit DESC
    LIMIT 10;
    """
)

# ============================================================
# Query 5: Monthly sales trend in 2017
# ============================================================
run_query(
    "Monthly sales trend in 2017",
    """
    SELECT strftime('%Y-%m', order_date) AS month,
           ROUND(SUM(sales), 2) AS monthly_sales
    FROM sales
    WHERE strftime('%Y', order_date) = '2017'
    GROUP BY month
    ORDER BY month;
    """
)

conn.close()