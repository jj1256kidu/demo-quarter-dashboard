import streamlit as st
import pandas as pd
import plotly.express as px

# Load data (replace this with your actual DataFrame)
df = pd.read_csv("quarterly_sales_summary.csv")  # Placeholder if using local file

st.set_page_config(page_title="Quarterly Sales Dashboard", layout="wide")

st.title("📊 Quarterly Sales Performance Dashboard")
st.markdown("""
Track and compare sales performance metrics like **Committed**, **Upside**, **Closed Won**, and their **deltas** across quarters and sales owners.
""")

# Filters
with st.sidebar:
    st.header("🔍 Filters")
    selected_owner = st.multiselect("Select Sales Owner(s):", options=df['Sales Owner'].unique(), default=df['Sales Owner'].unique())
    selected_quarter = st.multiselect("Select Quarter(s):", options=df['Quarter'].unique(), default=df['Quarter'].unique())

# Filter data
df_filtered = df[(df['Sales Owner'].isin(selected_owner)) & (df['Quarter'].isin(selected_quarter))]

# Metric Cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("💼 Total Committed (Current Week)", f"₹{df_filtered['Overall Committed (Current Week)'].sum():,.0f}")
col2.metric("📈 Total Upside (Current Week)", f"₹{df_filtered['Overall Upside (Current Week)'].sum():,.0f}")
col3.metric("✅ Closed Won (Current Week)", f"₹{df_filtered['Closed Won (Current Week)'].sum():,.0f}")
col4.metric("🔒 Committed + Closed Won (Current Week)", f"₹{df_filtered['Committed + Closed Won (Current Week)'].sum():,.0f}")

# Visualizations
st.subheader("📉 Delta Comparison Charts")

fig1 = px.bar(df_filtered, x="Sales Owner", y=["Committed Delta", "Upside Delta", "Closed Won Delta"],
              color_discrete_sequence=px.colors.qualitative.Set2,
              title="Weekly Delta Comparison by Sales Owner")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.sunburst(df_filtered, path=['Quarter', 'Sales Owner'], values='Committed + Closed Won (Current Week)',
                   title="Contribution by Quarter and Sales Owner")
st.plotly_chart(fig2, use_container_width=True)

# Detailed Data Table
st.subheader("📋 Detailed Summary Table")
st.dataframe(df_filtered.style.format("₹{:.0f}"))
