import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ============================================================
# STEP 1: Detect what kind of chart fits the data
# ============================================================
def detect_chart_type(df: pd.DataFrame) -> str:
    """
    Looks at the DataFrame and decides which chart type makes sense.
    Returns one of: 'bar', 'line', 'pie', 'table', 'kpi'
    """
    
    # If only 1 row and 1 column → it's a single number (KPI card)
    if df.shape[0] == 1 and df.shape[1] == 1:
        return "kpi"
    
    # If only 1 row but multiple columns → also KPI-like
    if df.shape[0] == 1:
        return "kpi"
    
    # If more than 20 rows → table is cleaner than a chart
    if df.shape[0] > 20:
        return "table"
    
    # Get column types
    columns = df.columns.tolist()
    
    # Check if there's a date/time column → line chart for trends
    for col in columns:
        col_lower = col.lower()
        if any(word in col_lower for word in ["date", "month", "year", "quarter", "week"]):
            return "line"
    
    # If 2-6 categories with values → pie chart works well
    if 2 <= df.shape[0] <= 6 and df.shape[1] == 2:
        return "pie"
    
    # Default for categorical comparisons → bar chart
    return "bar"


# ============================================================
# STEP 2: Generate the actual chart
# ============================================================
def generate_chart(df: pd.DataFrame, question: str = ""):
    """
    Takes a DataFrame and returns a Plotly figure.
    Returns None if data is empty.
    """
    
    if df.empty:
        return None
    
    chart_type = detect_chart_type(df)
    
    # Identify x (category) and y (value) columns
    # Usually first column = category, second = value
    columns = df.columns.tolist()
    
    if chart_type == "kpi":
        # Single number — make a big number display
        value = df.iloc[0, 0] if df.shape[1] == 1 else df.iloc[0].to_dict()
        fig = go.Figure(go.Indicator(
            mode="number",
            value=df.iloc[0, -1] if isinstance(df.iloc[0, -1], (int, float)) else 0,
            title={"text": question if question else "Result"},
        ))
        fig.update_layout(height=300)
        return fig
    
    elif chart_type == "table":
        # Too many rows — show as a styled table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df.columns),
                fill_color="#4F46E5",
                font=dict(color="white", size=13),
                align="left"
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color="#F3F4F6",
                align="left"
            )
        )])
        fig.update_layout(title=f"Results ({len(df)} rows)", height=500)
        return fig
    
    elif chart_type == "line":
        # Find the date column for x-axis
        date_col = None
        for col in columns:
            if any(w in col.lower() for w in ["date", "month", "year", "quarter"]):
                date_col = col
                break
        
        # Pick the first numeric column for y
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        y_col = numeric_cols[0] if numeric_cols else columns[1]
        
        fig = px.line(
            df, x=date_col, y=y_col,
            title=question if question else f"{y_col} over time",
            markers=True
        )
        fig.update_traces(line=dict(width=3, color="#4F46E5"))
        return fig
    
    elif chart_type == "pie":
        # x = labels, y = values
        fig = px.pie(
            df, names=columns[0], values=columns[1],
            title=question if question else f"{columns[1]} by {columns[0]}",
            hole=0.4  # makes it a donut chart — looks more modern
        )
        return fig
    
    else:  # bar chart (default)
        # Pick first non-numeric col for x, first numeric for y
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        non_numeric_cols = [c for c in columns if c not in numeric_cols]
        
        x_col = non_numeric_cols[0] if non_numeric_cols else columns[0]
        y_col = numeric_cols[0] if numeric_cols else columns[1]
        
        fig = px.bar(
            df, x=x_col, y=y_col,
            title=question if question else f"{y_col} by {x_col}",
            color=y_col,
            color_continuous_scale="Blues"
        )
        fig.update_layout(showlegend=False)
        return fig


# ============================================================
# STEP 3: Test it with sample data
# ============================================================
if __name__ == "__main__":
    
    # Test 1: Bar chart
    print("📊 Test 1: Bar chart (top products)")
    df1 = pd.DataFrame({
        "product_name": ["Canon Copier", "Fellowes Punch", "HP Designjet", "GBC DocuBind", "Hon Chair"],
        "total_sales": [61599.82, 27453.38, 18374.90, 17965.07, 16434.46]
    })
    fig1 = generate_chart(df1, "Top 5 products by sales")
    fig1.write_html("chart_test_bar.html", auto_open=True)
    
    # Test 2: Line chart (monthly trend)
    print("📈 Test 2: Line chart (monthly trend)")
    df2 = pd.DataFrame({
        "month": ["2017-01", "2017-02", "2017-03", "2017-04", "2017-05", "2017-06"],
        "monthly_sales": [43971, 20301, 58872, 36521, 44261, 52982]
    })
    fig2 = generate_chart(df2, "Monthly sales trend in 2017")
    fig2.write_html("chart_test_line.html", auto_open=True)
    
    # Test 3: Pie chart (small category split)
    print("🥧 Test 3: Pie chart (sales by region)")
    df3 = pd.DataFrame({
        "region": ["West", "East", "Central", "South"],
        "total_sales": [725457, 678781, 501239, 391721]
    })
    fig3 = generate_chart(df3, "Sales by region")
    fig3.write_html("chart_test_pie.html", auto_open=True)
    
    # Test 4: KPI (single value)
    print("🎯 Test 4: KPI card (single value)")
    df4 = pd.DataFrame({"total_customers": [793]})
    fig4 = generate_chart(df4, "Total unique customers")
    fig4.write_html("chart_test_kpi.html", auto_open=True)
    
    print("\n✅ All charts saved! Check your browser tabs.")

    