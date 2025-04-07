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

    # Calculate total values for current and previous week overall data
    total_current_week = df_current["Amount"].sum()
    total_previous_week = df_previous["Amount"].sum()

    # Display Overall Current and Previous Week totals
    st.markdown(f"### Overall Total (Current Week): ₹ {total_current_week:,.0f} Lakhs")
    st.markdown(f"### Overall Total (Previous Week): ₹ {total_previous_week:,.0f} Lakhs")

    # Sales Owner, Current Week, Previous Week, Delta Table
    st.markdown("### Sales Owner Comparison Table (in ₹ Lakhs)")

    # Group data by Sales Owner for both weeks
    df_current_summary = df_current.groupby('Sales Owner')['Amount'].sum().reset_index().rename(columns={'Amount': 'Overall (Current Week)'})
    df_previous_summary = df_previous.groupby('Sales Owner')['Amount'].sum().reset_index().rename(columns={'Amount': 'Overall (Previous Week)'})

    # Merge current and previous week data
    df_comparison = pd.merge(df_current_summary, df_previous_summary, on='Sales Owner', how='outer')

    # Calculate Delta
    df_comparison['Delta'] = df_comparison['Overall (Current Week)'] - df_comparison['Overall (Previous Week)']

    # Remove "NaN" entries (if any)
    df_comparison = df_comparison.dropna(subset=['Sales Owner'])

    # Display the table with Sales Owner, Current Week, Previous Week, and Delta
    st.dataframe(df_comparison, use_container_width=True)

else:
    st.warning("⚠️ Please upload an Excel file to continue.")
