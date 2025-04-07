import streamlit as st
import pandas as pd

# Sample Data Preparation (replace with your actual data)
data = {
    'Sales Owner': ['Anuj Bhargava', 'Ashish Kumar', 'Rajesh Loshali', 'Smriti Priya'],
    'Amount (Current Week)': [100, 200, 300, 400],
    'Amount (Previous Week)': [120, 180, 290, 380],
    'Delta': [-20, 20, 10, 20]
}

# Creating DataFrame
df = pd.DataFrame(data)

# Set the Streamlit page configuration
st.set_page_config(layout="wide", page_title="Weekly Commitment Dashboard")

# Sidebar filters for Sales Owner and Quarter
st.sidebar.title("Filters")
sales_owner_filter = st.sidebar.selectbox('Select Sales Owner', df['Sales Owner'].unique())
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
quarter_filter = st.sidebar.selectbox('Select Quarter', quarters)

# Header of the Dashboard
st.title("📊 Quarter Summary Dashboard")

# Tab Selection: Commitment, Upside, Closed Won, Overall
tab = st.selectbox("Select Metric for Comparison", ["Commitment", "Upside", "Closed Won", "Overall"])

# Filter data based on the selected sales owner (if "All" is selected, show all sales owners)
if sales_owner_filter != "All":
    filtered_df = df[df['Sales Owner'] == sales_owner_filter]
else:
    filtered_df = df

# Show different data depending on the selected tab
if tab == "Commitment":
    st.markdown("### 📝 Commitment Comparison (in ₹ Lakhs)")
    st.dataframe(filtered_df[['Sales Owner', 'Amount (Current Week)', 'Amount (Previous Week)', 'Delta']])

elif tab == "Upside":
    st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
    st.dataframe(filtered_df[['Sales Owner', 'Amount (Current Week)', 'Amount (Previous Week)', 'Delta']])

elif tab == "Closed Won":
    st.markdown("### ✅ Closed Won Comparison (in ₹ Lakhs)")
    st.dataframe(filtered_df[['Sales Owner', 'Amount (Current Week)', 'Amount (Previous Week)', 'Delta']])

elif tab == "Overall":
    st.markdown("### 📈 Overall Committed + Closed Won Comparison (in ₹ Lakhs)")
    # Calculate the overall (current week + previous week)
    filtered_df['Overall (Current Week)'] = filtered_df['Amount (Current Week)']
    filtered_df['Overall (Previous Week)'] = filtered_df['Amount (Previous Week)']
    filtered_df['Overall Delta'] = filtered_df['Overall (Current Week)'] - filtered_df['Overall (Previous Week)']
    st.dataframe(filtered_df[['Sales Owner', 'Overall (Current Week)', 'Overall (Previous Week)', 'Overall Delta']])

# Add a summary section below the tables
st.markdown("### 🔥 Summary Metrics")

total_commit_current_week = filtered_df['Amount (Current Week)'].sum()
total_commit_previous_week = filtered_df['Amount (Previous Week)'].sum()
total_delta = total_commit_current_week - total_commit_previous_week

st.markdown(f"**Total Commitment (Current Week):** ₹ {total_commit_current_week}")
st.markdown(f"**Total Commitment (Previous Week):** ₹ {total_commit_previous_week}")
st.markdown(f"**Total Delta:** ₹ {total_delta}")

# Optional: Add additional metrics for Upside or Closed Won similarly
# Example: Add total for Upside or Closed Won, if applicable, like:
# total_upside_current_week = filtered_df['Amount (Current Week)'].sum() (for Upside)
# st.markdown(f"**Total Upside (Current Week):** ₹ {total_upside_current_week}")

