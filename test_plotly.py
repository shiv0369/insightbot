import plotly.express as px
import pandas as pd

# Sample data
df = pd.DataFrame({
    "product": ["A", "B", "C", "D", "E"],
    "sales": [1200, 800, 1500, 600, 900]
})

# Make a bar chart
fig = px.bar(df, x="product", y="sales", title="Test Chart")

# Save as HTML and open in browser
fig.write_html("test_chart.html", auto_open=True)
print("✅ Chart saved as test_chart.html and opened in your browser.")