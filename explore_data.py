import pandas as pd

# Load the CSV into a Pandas DataFrame
# Note: this dataset uses a special encoding ('latin-1') because it has some non-standard characters
df = pd.read_csv("data/superstore.csv", encoding="latin-1")

# 1. How many rows and columns?
print("Shape (rows, columns):", df.shape)
print()

# 2. What columns do we have?
print("Columns:")
print(df.columns.tolist())
print()

# 3. What does the data look like?
print("First 3 rows:")
print(df.head(3))
print()

# 4. What types are each column?
print("Data types:")
print(df.dtypes)
print()

# 5. Any missing values?
print("Missing values per column:")
print(df.isnull().sum())