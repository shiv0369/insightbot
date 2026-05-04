import pandas as pd
import sqlite3
import os

# ============================================================
# STEP 1: Load the CSV
# ============================================================
print("📂 Loading CSV...")
df = pd.read_csv("data/superstore.csv", encoding="latin-1")
print(f"   Loaded {len(df)} rows.")

# ============================================================
# STEP 2: Clean column names
# Make them SQL-friendly: lowercase, underscores instead of spaces/dashes
# ============================================================
print("🧹 Cleaning column names...")
df.columns = (
    df.columns
    .str.strip()                  # remove leading/trailing spaces
    .str.lower()                  # lowercase
    .str.replace(" ", "_")        # spaces → underscores
    .str.replace("-", "_")        # dashes → underscores
)
print("   New columns:", df.columns.tolist())

# ============================================================
# STEP 3: Convert date columns to proper datetime
# (this helps with date-based SQL queries later)
# ============================================================
print("📅 Converting date columns...")
df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y", errors="coerce")
df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y", errors="coerce")

# ============================================================
# STEP 4: Create the SQLite database and load the data
# ============================================================
print("💾 Creating SQLite database...")

# Make sure the data folder exists
os.makedirs("data", exist_ok=True)

# Connect to SQLite — if the .db file doesn't exist, it will be created
db_path = "data/superstore.db"
conn = sqlite3.connect(db_path)

# Write the DataFrame to a table called 'sales'
# if_exists='replace' means: if the table already exists, overwrite it
df.to_sql("sales", conn, if_exists="replace", index=False)

print(f"   Database saved at: {db_path}")

# ============================================================
# STEP 5: Verify by running a quick test query
# ============================================================
print("\n🔍 Running test query...")
cursor = conn.cursor()

# Count rows
cursor.execute("SELECT COUNT(*) FROM sales")
row_count = cursor.fetchone()[0]
print(f"   Total rows in 'sales' table: {row_count}")

# Show first 3 rows
cursor.execute("SELECT order_id, customer_name, sales, region FROM sales LIMIT 3")
rows = cursor.fetchall()
print("   Sample rows:")
for row in rows:
    print("    ", row)

conn.close()
print("\n✅ Done! Your database is ready.")