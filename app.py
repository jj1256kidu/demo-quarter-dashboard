import streamlit as st
import pandas as pd

# Function to load data from the file
def load_data(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    df_current = pd.read_excel(xls, sheet_name="Raw_Data")
    df_previous = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")
    return df_current, df_previous

# Preprocessing to extract totals for the required fields
def get_totals(df, status_type):
    filtered_data = df[df['Status'] == status_type]
    total = filtered_data['Amount'].sum()
    return total

# Function to clean and preprocess the Sales Owner column
def clean_sales_owner_column(df):
    df['Sales Owner'] = df['Sales Owner'].str.strip()
    df['Sales Owner'] = df['Sales Owner'].fillna('Unknown')
    return df

# Ensure Amount is numeric and replace errors with 0
def convert_to_numeric(df):
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    return df

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

# Function to generate the table view for Sales Owners and their data
def display_sales_owner_table(df_current, df_previous, selected_status, selected_quarter, selected_range):
    # Clean Sales Owner columns to handle NaN and strip values
    df_current = clean_sales_owner_column(df_current)
    df_previous = clean_sales_owner_column(df_previous)

    # Ensure 'Amount' column is numeric
    df_current = convert_to_numeric(df_current)
    df_previous = convert_to_numeric(df_previous)

    # Filter by Status and Quarter
    if selected_quarter != "All":
        df_current = df_current[df_current["Quarter"] == selected_quarter]
        df_previous = df_previous[df_previous["Quarter"] == selected_quarter]

    if selected_status != "All":
        df_current = df_current[df_current["Status"] == selected_status]
        df_previous = df_previous[df_previous["Status"] == selected_status]

    # Filter by Range (For Strong Upside, apply a probability range)
    if selected_range != "All":
        df_current = df_current[df_current["Probability"] == selected_range]
        df_previous = df_previous[df_previous["Probability"] == selected_range]

    # Extract sales owner names (after cleaning)
    sales_owners = sorted(set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique()))

    data = []

    # Loop through each sales owner and calculate the totals
    for owner in sales_owners:
        committed_current = get_totals(df_current[df_current['Sales Owner'] == owner], "Committed for the Month")
        committed_previous = get_totals(df_previous[df_previous['Sales Owner'] == owner], "Committed for the Month")
        upside_current = get_totals(df_current[df_current['Sales Owner'] == owner], "Upside for the Month")
        upside_previous = get_totals(df_previous[df_previous['Sales Owner'] == owner], "Upside for the Month")
        closed_won_current = get_totals(df_current[df_current['Sales Owner'] == owner], "Closed Won")
        closed_won_previous = get_totals(df_previous[df_previous['Sales Owner'] == owner], "Closed Won")
        
        # Calculate the delta for each
        delta_committed = committed_current - committed_previous
        delta_upside = upside_current - upside_previous
        delta_closed_won = closed_won_current - closed_won_previous

        data.append({
            "Sales Owner": owner,
            "Committed (Current Week)": committed_current,
            "Committed (Previous Week)": committed_previous,
            "∆ Committed": delta_committed,
            "Upside (Current Week)": upside_current,
            "Upside (Previous Week)": upside_previous,
            "∆ Upside": delta_upside,
            "Closed Won (Current Week)": closed_won_current,
            "Closed Won (Previous Week)": closed_won_previous,
            "∆ Closed Won": delta_closed_won
        })

    df_table = pd.DataFrame(data)

    # Highlight deltas based on the sign
    def highlight_delta(val):
        if val > 0:
            return 'color: green'
        elif val < 0:
            return 'color: red'
        return 'color: black'

    # Apply styling to the DataFrame
    st.dataframe(df_table.style.applymap(highlight_delta, subset=["∆ Committed", "∆ Upside", "∆ Closed Won"]), use_container_width=True)

def main():
    # Page setup for file uploading and filtering
    st.set_page_config(page_title="Sales Comparison Dashboard", layout="wide")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file:
        df_current, df_previous = load_data(uploaded_file)
        
        # Add filters for status, quarter, and range
        status_options = ["All", "Committed for the Month", "Upside for the Month", "Closed Won"]
        selected_status = st.selectbox("Select Status", status_options)
        
        quarters = sorted(df_current["Quarter"].unique())
        selected_quarter = st.selectbox("Select Quarter", ["All"] + quarters)
        
        range_options = ["All", "Strong Upside", "Medium Upside", "Low Upside"]
        selected_range = st.selectbox("Select Probability Range", range_options)

        display_sales_cards(df_current, df_previous)
        display_sales_owner_table(df_current, df_previous, selected_status, selected_quarter, selected_range)

if __name__ == "__main__":
    main()
