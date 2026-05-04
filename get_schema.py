import sqlite3

conn = sqlite3.connect("data/superstore.db")
cursor = conn.cursor()

# Get column info for the 'sales' table
cursor.execute("PRAGMA table_info(sales);")
columns = cursor.fetchall()

print("Columns in 'sales' table:")
print("-" * 50)
for col in columns:
    # col format: (id, name, type, not_null, default, primary_key)
    print(f"  {col[1]:<20} {col[2]}")

# Also get a few sample rows to give the LLM context
cursor.execute("SELECT * FROM sales LIMIT 2")
sample_rows = cursor.fetchall()

print("\nSample rows (for LLM context):")
print(sample_rows)

conn.close()