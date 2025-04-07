import streamlit as st
import pandas as pd

# Function to load data from the file
def load_data(uploaded_file):
    # Load the Excel file
    xls = pd.ExcelFile(uploaded_file)
    df_current = pd.read_excel(xls, sheet_name="Raw_Data")
    df_previous = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")
    return df_current, df_previous

# Preprocessing to extract totals for the required fields
def get_totals(df, status_type):
    # Filter the data by Status Type (e.g., Committed for the Month, Upside for the Month, Closed Won)
    filtered_data = df[df['Status'] == status_type]
    total = filtered_data['Amount'].sum()
    return total

# Function to render the sales cards
def display_sales_cards(df_current, df_previous):
    # Committed Data
    committed_current = get_totals(df_current, "Committed for the Month")
    committed_previous = get_totals(df_previous, "Committed for the Month")
    committed_delta = committed_current - committed_previous

    # Upside Data
    upside_current = get_totals(df_current, "Upside for the Month")
    upside_previous = get_totals(df_previous, "Upside for the Month")
    upside_delta = upside_current - upside_previous

    # Closed Won Data
    closed_won_current = get_totals(df_current, "Closed Won")
    closed_won_previous = get_totals(df_previous, "Closed Won")
    closed_won_delta = closed_won_current - closed_won_previous

    # Overall Committed Data (Committed + Closed Won)
    overall_committed_current = committed_current + closed_won_current
    overall_committed_previous = committed_previous + closed_won_previous
    overall_committed_delta = overall_committed_current - overall_committed_previous

    # Display Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Committed Data")
        st.metric(label="Total (Current Week)", value=f"₹ {committed_current/1e5:.1f}L", delta=f"₹ {committed_delta/1e5:.1f}L")
        
    with col2:
        st.markdown("### Upside Data")
        st.metric(label="Total (Current Week)", value=f"₹ {upside_current/1e5:.1f}L", delta=f"₹ {upside_delta/1e5:.1f}L")

    with col3:
        st.markdown("### Closed Won")
        st.metric(label="Total (Current Week)", value=f"₹ {closed_won_current/1e5:.1f}L", delta=f"₹ {closed_won_delta/1e5:.1f}L")
        
    with col4:
        st.markdown("### Overall Committed Data")
        st.metric(label="Total (Current Week)", value=f"₹ {overall_committed_current/1e5:.1f}L", delta=f"₹ {overall_committed_delta/1e5:.1f}L")

# Streamlit Application
def main():
    st.title("Sales Dashboard")

    # File upload
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df_current, df_previous = load_data(uploaded_file)
        display_sales_cards(df_current, df_previous)

if __name__ == "__main__":
    main()
