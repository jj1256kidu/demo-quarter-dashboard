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

# Function to filter data based on selected filters
def filter_data(df, selected_quarter, selected_sales_owner, status_type):
    if selected_quarter != "All":
        df = df[df["Quarter"] == selected_quarter]
    if selected_sales_owner != "All":
        df = df[df["Sales Owner"] == selected_sales_owner]
    return df[df["Status"] == status_type]

# Function to aggregate data for each sales owner or function
def agg_amount(df):
    return df.groupby("Sales Owner")["Amount"].sum().reset_index()

# Function to display the comparison table for sales owners
def display_sales_owner_table(df_current, df_previous, selected_quarter, selected_sales_owner):
    # Filter data for current and previous week
    df_commit_current = filter_data(df_current, selected_quarter, selected_sales_owner, "Committed for the Month")
    df_commit_previous = filter_data(df_previous, selected_quarter, selected_sales_owner, "Committed for the Month")
    df_upside_current = filter_data(df_current, selected_quarter, selected_sales_owner, "Upside for the Month")
    df_upside_previous = filter_data(df_previous, selected_quarter, selected_sales_owner, "Upside for the Month")
    df_closed_current = filter_data(df_current, selected_quarter, selected_sales_owner, "Closed Won")
    df_closed_previous = filter_data(df_previous, selected_quarter, selected_sales_owner, "Closed Won")

    # Aggregate the data
    df_commit_current = agg_amount(df_commit_current).rename(columns={"Amount": "Committed (Current Week)"})
    df_commit_previous = agg_amount(df_commit_previous).rename(columns={"Amount": "Committed (Previous Week)"})
    df_upside_current = agg_amount(df_upside_current).rename(columns={"Amount": "Upside (Current Week)"})
    df_upside_previous = agg_amount(df_upside_previous).rename(columns={"Amount": "Upside (Previous Week)"})
    df_closed_current = agg_amount(df_closed_current).rename(columns={"Amount": "Closed Won (Current Week)"})
    df_closed_previous = agg_amount(df_closed_previous).rename(columns={"Amount": "Closed Won (Previous Week)"})

    # Merge all data
    df = pd.merge(df_commit_current, df_commit_previous, on="Sales Owner", how="outer")
    df = pd.merge(df, df_upside_current, on="Sales Owner", how="outer")
    df = pd.merge(df, df_upside_previous, on="Sales Owner", how="outer")
    df = pd.merge(df, df_closed_current, on="Sales Owner", how="outer")
    df = pd.merge(df, df_closed_previous, on="Sales Owner", how="outer")

    # Calculate deltas
    df["∆ Committed"] = df["Committed (Current Week)"] - df["Committed (Previous Week)"]
    df["∆ Upside"] = df["Upside (Current Week)"] - df["Upside (Previous Week)"]
    df["∆ Closed Won"] = df["Closed Won (Current Week)"] - df["Closed Won (Previous Week)"]
    df["∆ Overall Committed + Closed Won (Current Week)"] = (df["Committed (Current Week)"] + df["Closed Won (Current Week)"])
    df["∆ Overall Committed + Closed Won (Previous Week)"] = (df["Committed (Previous Week)"] + df["Closed Won (Previous Week)"])
    df["∆ Overall Committed + Closed Won Delta"] = df["∆ Overall Committed + Closed Won (Current Week)"] - df["∆ Overall Committed + Closed Won (Previous Week)"]
    
    df.fillna(0, inplace=True)

    # Apply styling to highlight deltas
    df_styled = df.style.applymap(highlight_delta, subset=["∆ Committed", "∆ Upside", "∆ Closed Won", "∆ Overall Committed + Closed Won Delta"])

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

        # Filter options for quarter and sales owner
        quarters = sorted(set(df_current["Quarter"].unique()) | set(df_previous["Quarter"].unique()))
        selected_quarter = st.selectbox("Select Quarter", quarters)

        sales_owners = sorted(set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique()))
        selected_sales_owner = st.selectbox("Select Sales Owner", ["All"] + sales_owners)

        # Display the sales owner comparison table
        display_sales_owner_table(df_current, df_previous, selected_quarter, selected_sales_owner)

if __name__ == "__main__":
    main()
