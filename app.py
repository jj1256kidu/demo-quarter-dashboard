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

# Function to filter data based on selected status
def filter_data(df, status_type):
    return df[df["Status"] == status_type]

# Function to aggregate data for each sales owner
def agg_amount(df):
    return df.groupby("Sales Owner")["Amount"].sum().reset_index()

# Function to display the comparison table for sales owners
def display_sales_owner_table(df_current, df_previous, selected_status):
    # Filter data for current and previous week based on the selected status
    df_current_filtered = filter_data(df_current, selected_status)
    df_previous_filtered = filter_data(df_previous, selected_status)

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

        # Filter options for status (Committed or Upside)
        status_options = ["Committed for the Month", "Upside for the Month"]
        selected_status = st.selectbox("Select Status", status_options)

        # Display the sales owner comparison table
        display_sales_owner_table(df_current, df_previous, selected_status)

if __name__ == "__main__":
    main()
