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
    
    # Select Sheets for current and previous week data
    selected_current_sheet = st.sidebar.selectbox("Select Current Week Sheet", sheet_names)
    selected_previous_sheet = st.sidebar.selectbox("Select Previous Week Sheet", sheet_names)
    
    df_current = pd.read_excel(xls, sheet_name=selected_current_sheet)
    df_previous = pd.read_excel(xls, sheet_name=selected_previous_sheet)

    # Preprocess the data
    def preprocess(df):
        df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
        df["Quarter"] = df["Quarter"].astype(str).str.strip()
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        return df

    df_current = preprocess(df_current)
    df_previous = preprocess(df_previous)

    # Filter options for Sales Owner and Quarter
    sales_owner_filter = st.sidebar.selectbox('Select Sales Owner', ['All'] + df_current['Sales Owner'].unique().tolist())
    quarters = ['All'] + df_current['Quarter'].unique().tolist()
    quarter_filter = st.sidebar.selectbox('Select Quarter', quarters)

    # Filter data based on selections
    if sales_owner_filter != "All":
        df_current = df_current[df_current['Sales Owner'] == sales_owner_filter]
        df_previous = df_previous[df_previous['Sales Owner'] == sales_owner_filter]
    if quarter_filter != "All":
        df_current = df_current[df_current['Quarter'] == quarter_filter]
        df_previous = df_previous[df_previous['Quarter'] == quarter_filter]

    # Header of the Dashboard
    st.title("📊 Quarter Summary Dashboard")

    # Tab Selection: Commitment, Upside, Closed Won, Overall
    tab = st.selectbox("Select Metric for Comparison", ["Commitment", "Upside", "Closed Won", "Overall"])

    # Display different data depending on the selected tab
    if tab == "Commitment":
        st.markdown("### 📝 Commitment Comparison (in ₹ Lakhs)")
        df_commit_current = df_current[df_current['Status'] == 'Committed for the Month']
        df_commit_previous = df_previous[df_previous['Status'] == 'Committed for the Month']
        st.dataframe(df_commit_current[['Sales Owner', 'Amount']], use_container_width=True)
        st.dataframe(df_commit_previous[['Sales Owner', 'Amount']], use_container_width=True)

    elif tab == "Upside":
        st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
        df_upside_current = df_current[df_current['Status'] == 'Upside for the Month']
        df_upside_previous = df_previous[df_previous['Status'] == 'Upside for the Month']
        st.dataframe(df_upside_current[['Sales Owner', 'Amount']], use_container_width=True)
        st.dataframe(df_upside_previous[['Sales Owner', 'Amount']], use_container_width=True)

    elif tab == "Closed Won":
        st.markdown("### ✅ Closed Won Comparison (in ₹ Lakhs)")
        df_closed_current = df_current[df_current['Status'] == 'Closed Won']
        df_closed_previous = df_previous[df_previous['Status'] == 'Closed Won']
        st.dataframe(df_closed_current[['Sales Owner', 'Amount']], use_container_width=True)
        st.dataframe(df_closed_previous[['Sales Owner', 'Amount']], use_container_width=True)

    elif tab == "Overall":
        st.markdown("### 📈 Overall Committed + Closed Won Comparison (in ₹ Lakhs)")
        df_current['Overall (Current Week)'] = df_current['Amount'] + df_current['Amount']
        df_previous['Overall (Previous Week)'] = df_previous['Amount'] + df_previous['Amount']
        st.dataframe(df_current[['Sales Owner', 'Overall (Current Week)']], use_container_width=True)
        st.dataframe(df_previous[['Sales Owner', 'Overall (Previous Week)']], use_container_width=True)

    # Add a summary section below the tables
    st.markdown("### 🔥 Summary Metrics")

    total_commit_current_week = df_current['Amount'].sum()
    total_commit_previous_week = df_previous['Amount'].sum()
    total_delta = total_commit_current_week - total_commit_previous_week

    st.markdown(f"**Total Commitment (Current Week):** ₹ {total_commit_current_week}")
    st.markdown(f"**Total Commitment (Previous Week):** ₹ {total_commit_previous_week}")
    st.markdown(f"**Total Delta:** ₹ {total_delta}")
