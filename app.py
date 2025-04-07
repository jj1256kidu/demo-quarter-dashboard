import streamlit as st
import pandas as pd
import numpy as np

# Helper function to format the amounts
def format_amount(x):
    try:
        if pd.isna(x) or x == 0:
            return "₹0L"
        value = float(str(x).replace('₹', '').replace('L', '').replace(',', ''))
        return f"₹{int(value)}L"
    except:
        return "₹0L"

# Ensure data is loaded
def load_data():
    if 'df_current' not in st.session_state or 'df_previous' not in st.session_state:
        # Load the current and previous week data here
        # Assuming the dataframe is already loaded into session state
        return pd.DataFrame(), pd.DataFrame()
    return st.session_state.df_current, st.session_state.df_previous

# Function to calculate the key metrics for display
def calculate_kpi(df_current, df_previous):
    # Filter the data based on the "Status" for "Committed for the Month" and "Upside for the Month"
    committed_current_week = df_current[df_current['Status'] == 'Committed for the Month']['Amount'].sum()
    committed_previous_week = df_previous[df_previous['Status'] == 'Committed for the Month']['Amount'].sum()
    committed_delta = committed_current_week - committed_previous_week
    
    upside_current_week = df_current[df_current['Status'] == 'Upside for the Month']['Amount'].sum()
    upside_previous_week = df_previous[df_previous['Status'] == 'Upside for the Month']['Amount'].sum()
    upside_delta = upside_current_week - upside_previous_week
    
    return committed_current_week, committed_previous_week, committed_delta, upside_current_week, upside_previous_week, upside_delta

def display_kpi(committed_current_week, committed_previous_week, committed_delta, upside_current_week, upside_previous_week, upside_delta):
    st.markdown("# Key Metrics (KPI)")
    col1, col2, col3 = st.columns(3)

    # Committed Data KPI
    with col1:
        st.markdown("### Committed Data")
        st.markdown(f"**₹{format_amount(committed_current_week)}**")
        st.markdown(f"Current Week Total: **₹{format_amount(committed_current_week)}**")
        st.markdown(f"Previous Week Total: **₹{format_amount(committed_previous_week)}**")
        st.markdown(f"Delta: **₹{format_amount(committed_delta)}**")

    # Upside Data KPI
    with col2:
        st.markdown("### Upside Data")
        st.markdown(f"**₹{format_amount(upside_current_week)}**")
        st.markdown(f"Current Week Total: **₹{format_amount(upside_current_week)}**")
        st.markdown(f"Previous Week Total: **₹{format_amount(upside_previous_week)}**")
        st.markdown(f"Delta: **₹{format_amount(upside_delta)}**")

    # Total KPI
    with col3:
        total_current_week = committed_current_week + upside_current_week
        total_previous_week = committed_previous_week + upside_previous_week
        total_delta = total_current_week - total_previous_week
        
        st.markdown("### Overall Committed Data (Committed + Upside)")
        st.markdown(f"**₹{format_amount(total_current_week)}**")
        st.markdown(f"Current Week Total: **₹{format_amount(total_current_week)}**")
        st.markdown(f"Previous Week Total: **₹{format_amount(total_previous_week)}**")
        st.markdown(f"Delta: **₹{format_amount(total_delta)}**")

def main():
    # Load the data
    df_current, df_previous = load_data()

    if df_current.empty or df_previous.empty:
        st.error("Please upload the data for both Current Week and Previous Week.")
        return
    
    # Calculate KPI
    committed_current_week, committed_previous_week, committed_delta, upside_current_week, upside_previous_week, upside_delta = calculate_kpi(df_current, df_previous)

    # Display KPI metrics
    display_kpi(committed_current_week, committed_previous_week, committed_delta, upside_current_week, upside_previous_week, upside_delta)

if __name__ == "__main__":
    main()
