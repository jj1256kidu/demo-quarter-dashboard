import streamlit as st
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Weekly Commitment Dashboard")

# Sidebar filters for Sales Owner and Quarter
st.sidebar.title("Filters")

# File Upload
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the Excel file
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    st.sidebar.write(f"Sheets available: {sheet_names}")
    
    # Select Sheet
    selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)
    df = pd.read_excel(xls, sheet_name=selected_sheet)

    # Preprocess the data
    def preprocess(df):
        df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
        df["Quarter"] = df["Quarter"].astype(str).str.strip()
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        return df

    df = preprocess(df)

    # Filter options for Sales Owner and Quarter
    sales_owner_filter = st.sidebar.selectbox('Select Sales Owner', ['All'] + df['Sales Owner'].unique().tolist())
    quarters = ['All'] + df['Quarter'].unique().tolist()
    quarter_filter = st.sidebar.selectbox('Select Quarter', quarters)

    # Filter data based on selections
    if sales_owner_filter != "All":
        df = df[df['Sales Owner'] == sales_owner_filter]
    if quarter_filter != "All":
        df = df[df['Quarter'] == quarter_filter]

    # Header of the Dashboard
    st.title("📊 Quarter Summary Dashboard")

    # Tab Selection: Commitment, Upside, Closed Won, Overall
    tab = st.selectbox("Select Metric for Comparison", ["Commitment", "Upside", "Closed Won", "Overall"])

    # Display different data depending on the selected tab
    if tab == "Commitment":
        st.markdown("### 📝 Commitment Comparison (in ₹ Lakhs)")
        st.dataframe(df[['Sales Owner', 'Amount (Current Week)', 'Amount (Previous Week)', 'Delta']])

    elif tab == "Upside":
        st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
        st.dataframe(df[['Sales Owner', 'Amount (Current Week)', 'Amount (Previous Week)', 'Delta']])

    elif tab == "Closed Won":
        st.markdown("### ✅ Closed Won Comparison (in ₹ Lakhs)")
        st.dataframe(df[['Sales Owner', 'Amount (Current Week)', 'Amount (Previous Week)', 'Delta']])

    elif tab == "Overall":
        st.markdown("### 📈 Overall Committed + Closed Won Comparison (in ₹ Lakhs)")
        # Calculate the overall (current week + previous week)
        df['Overall (Current Week)'] = df['Amount (Current Week)'] + df['Amount (Previous Week)']
        df['Overall (Previous Week)'] = df['Amount (Previous Week)'] + df['Amount (Current Week)']
        df['Overall Delta'] = df['Overall (Current Week)'] - df['Overall (Previous Week)']
        st.dataframe(df[['Sales Owner', 'Overall (Current Week)', 'Overall (Previous Week)', 'Overall Delta']])

    # Add a summary section below the tables
    st.markdown("### 🔥 Summary Metrics")

    total_commit_current_week = df['Amount (Current Week)'].sum()
    total_commit_previous_week = df['Amount (Previous Week)'].sum()
    total_delta = total_commit_current_week - total_commit_previous_week

    st.markdown(f"**Total Commitment (Current Week):** ₹ {total_commit_current_week}")
    st.markdown(f"**Total Commitment (Previous Week):** ₹ {total_commit_previous_week}")
    st.markdown(f"**Total Delta:** ₹ {total_delta}")

