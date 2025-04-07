import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(page_title="Sales Performance Dashboard", page_icon="📊", layout="wide")

# Helper Functions
def format_amount(x):
    try:
        if pd.isna(x) or x == 0:
            return "₹0L"
        value = float(str(x).replace('₹', '').replace('L', '').replace(',', ''))
        return f"₹{int(value)}L"
    except:
        return "₹0L"

def format_percentage(x):
    try:
        if pd.isna(x) or x == 0:
            return "0%"
        value = float(str(x).replace('%', '').strip())
        return f"{int(value)}%"
    except:
        return "0%"

def calculate_delta(current, previous):
    delta = current - previous
    return delta, "green" if delta > 0 else ("red" if delta < 0 else "black")

# Data Processing Function
@st.cache_data
def process_data(df):
    df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'], errors='coerce')
    df['Month'] = df['Expected Close Date'].dt.strftime('%B')
    df['Year'] = df['Expected Close Date'].dt.year
    df['Quarter'] = df['Expected Close Date'].dt.quarter.map({1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'})
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    return df

# Displaying the Key Metrics (KPI)
def display_kpi_metrics(df_current, df_previous):
    # Metrics: Committed, Upside, Closed Won, Overall Committed
    metrics = ["Committed for the Month", "Upside for the Month", "Closed Won", "Overall Committed Data"]
    
    st.markdown("### 📝 Key Metrics (KPI)")

    for metric in metrics:
        # Get the current and previous week totals for each metric
        current_total = df_current[df_current['Status'] == metric]['Amount'].sum() / 100000
        previous_total = df_previous[df_previous['Status'] == metric]['Amount'].sum() / 100000
        delta, delta_color = calculate_delta(current_total, previous_total)
        
        st.markdown(f"**{metric}**: <span style='font-size:20px; color: {delta_color};'>₹ {current_total:,.0f} Lakh</span> (Current Week), <span style='font-size:20px;'>₹ {previous_total:,.0f} Lakh</span> (Previous Week), <span style='font-size:20px; color: {delta_color};'>Δ ₹ {delta:,.0f} Lakh</span>", unsafe_allow_html=True)

# Sales Owner Data Table Display
def display_sales_owner_data(df_current, df_previous):
    sales_owners = sorted(set(df_current['Sales Owner'].unique()) | set(df_previous['Sales Owner'].unique()))
    st.markdown("### 📊 Sales Owner Data Comparison")
    sales_data = []

    for owner in sales_owners:
        current_value = df_current[df_current['Sales Owner'] == owner]['Amount'].sum() / 100000
        previous_value = df_previous[df_previous['Sales Owner'] == owner]['Amount'].sum() / 100000
        delta, delta_color = calculate_delta(current_value, previous_value)
        sales_data.append([owner, current_value, previous_value, delta])

    # Create DataFrame for display
    sales_df = pd.DataFrame(sales_data, columns=["Sales Owner", "Current Week", "Previous Week", "Delta"])
    sales_df['Delta'] = sales_df['Delta'].apply(lambda x: f"₹{int(x):,.0f}")
    
    # Display table
    st.dataframe(sales_df, use_container_width=True)

# Main function to handle the dashboard view
def main():
    st.title("📊 Sales Performance Dashboard")
    
    # Upload file input
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    
    if uploaded_file:
        # Read Excel file
        xls = pd.ExcelFile(uploaded_file)
        df_current = pd.read_excel(xls, sheet_name="Current Week")
        df_previous = pd.read_excel(xls, sheet_name="Previous Week")

        # Process the data
        df_current = process_data(df_current)
        df_previous = process_data(df_previous)

        # Display Key Metrics (KPI)
        display_kpi_metrics(df_current, df_previous)

        # Display Sales Owner Data Comparison Table
        display_sales_owner_data(df_current, df_previous)

if __name__ == "__main__":
    main()
