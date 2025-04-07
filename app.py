import streamlit as st
import pandas as pd

# Function to highlight deltas with colors (green for +, red for -, black for 0)
def highlight_delta(val):
    if isinstance(val, (int, float)):  # Only apply color to numerical values
        if val > 0:
            return 'color: green'
        elif val < 0:
            return 'color: red'
        else:
            return 'color: black'
    return ''

# Function to preprocess data
def preprocess(df):
    df["Quarter"] = df["Quarter"].astype(str).str.strip()
    df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df

# Function to filter data based on selected status and quarter
def filter_data(df, status_type, selected_quarter):
    df_filtered = df[df["Status"] == status_type]
    if selected_quarter != "All":
        df_filtered = df_filtered[df_filtered["Quarter"] == selected_quarter]
    return df_filtered

# Function to aggregate data for each sales owner
def agg_amount(df):
    return df.groupby("Sales Owner")["Amount"].sum().reset_index()

# Function to display the comparison table for sales owners
def display_sales_owner_table(df_current, df_previous, selected_status, selected_quarter):
    # Filter data for current and previous week based on the selected status and quarter
    df_current_filtered = filter_data(df_current, selected_status, selected_quarter)
    df_previous_filtered = filter_data(df_previous, selected_status, selected_quarter)

    # Aggregate the data
    df_current_agg = agg_amount(df_current_filtered).rename(columns={"Amount": "Current Week"})
    df_previous_agg = agg_amount(df_previous_filtered).rename(columns={"Amount": "Previous Week"})

    # Merge the data for current and previous week
    df = pd.merge(df_current_agg, df_previous_agg, on="Sales Owner", how="outer").fillna(0)

    # Calculate delta
    df["Delta"] = df["Current Week"] - df["Previous Week"]

    # Apply styling to highlight deltas
    df_styled = df.style.applymap(highlight_delta, subset=["Delta"])

    # Display the table with Streamlit
    st.dataframe(df_styled, use_container_width=True)

# Streamlit app
def main():
    st.title("📊 Sales Owner Comparison Dashboard")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file:
        # Load the Excel file
        xls = pd.ExcelFile(uploaded_file)
        df_current = pd.read_excel(xls, sheet_name="Raw_Data")
        df_previous = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Preprocess data
        df_current = preprocess(df_current)
        df_previous = preprocess(df_previous)

        # Filter options for status (Committed or Upside) and quarter
        status_options = ["Committed for the Month", "Upside for the Month", "Closed Won"]
        
        # Add unique keys for each selectbox
        selected_status = st.selectbox("Select Status", status_options, key="status_selectbox")
        
        # Quarter filter (including "All" option to show all quarters)
        quarters = ["All"] + sorted(df_current["Quarter"].unique().tolist())
        
        # Use st.columns to place filters in the same row
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_status = st.selectbox("Select Status", status_options, key="status_selectbox")
        with col2:
            selected_quarter = st.selectbox("Select Quarter", quarters, key="quarter_selectbox")

        # Calculating total for each category (Committed, Upside, Closed Won)
        def calculate_totals(df_current, df_previous, selected_status, selected_quarter):
            df_current_filtered = filter_data(df_current, selected_status, selected_quarter)
            df_previous_filtered = filter_data(df_previous, selected_status, selected_quarter)

            df_current_total = agg_amount(df_current_filtered)["Amount"].sum()
            df_previous_total = agg_amount(df_previous_filtered)["Amount"].sum()
            delta = df_current_total - df_previous_total
            return df_current_total, df_previous_total, delta

        # Get totals for each status
        committed_current, committed_previous, committed_delta = calculate_totals(df_current, df_previous, "Committed for the Month", selected_quarter)
        upside_current, upside_previous, upside_delta = calculate_totals(df_current, df_previous, "Upside for the Month", selected_quarter)
        closed_won_current, closed_won_previous, closed_won_delta = calculate_totals(df_current, df_previous, "Closed Won", selected_quarter)

        # Overall Committed + Closed Won
        overall_committed_current = committed_current + closed_won_current
        overall_committed_previous = committed_previous + closed_won_previous
        overall_committed_delta = overall_committed_current - overall_committed_previous

        # Display the totals
        st.markdown("### 📝 Total Overview (in ₹ Lakhs)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Committed", f"₹ {committed_current:,.0f} (Current Week)", f"₹ {committed_delta:,.0f} (Delta)")
        with col2:
            st.metric("Upside", f"₹ {upside_current:,.0f} (Current Week)", f"₹ {upside_delta:,.0f} (Delta)")
        with col3:
            st.metric("Closed Won", f"₹ {closed_won_current:,.0f} (Current Week)", f"₹ {closed_won_delta:,.0f} (Delta)")
        with col4:
            st.metric("Overall Committed + Closed Won", f"₹ {overall_committed_current:,.0f} (Current Week)", f"₹ {overall_committed_delta:,.0f} (Delta)")

        # Display the sales owner comparison table
        display_sales_owner_table(df_current, df_previous, selected_status, selected_quarter)

if __name__ == "__main__":
    main()
