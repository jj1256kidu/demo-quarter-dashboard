import streamlit as st
import pandas as pd

# Function to preprocess the data
def preprocess(df):
    df["Quarter"] = df["Quarter"].astype(str).str.strip()
    df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df

# Function to filter data for "Committed for the Month"
def filter_committed(df):
    return df[df["Status"] == "Committed for the Month"]

# Function to aggregate the data
def agg_amount(df):
    return df.groupby("Sales Owner")["Amount"].sum().reset_index()

# Function to display the sales owner table with current week, previous week, and delta
def display_committed_for_month(df_current, df_previous):
    # Filter the data for "Committed for the Month"
    df_current_filtered = filter_committed(df_current)
    df_previous_filtered = filter_committed(df_previous)

    # Aggregate the data for current and previous week
    df_current_agg = agg_amount(df_current_filtered).rename(columns={"Amount": "Current Week"})
    df_previous_agg = agg_amount(df_previous_filtered).rename(columns={"Amount": "Previous Week"})

    # Get all unique sales owners from both current and previous week data
    all_sales_owners = sorted(set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique()))

    # Create a dataframe with all sales owners, even those with no data
    all_sales_owners_df = pd.DataFrame({"Sales Owner": all_sales_owners})

    # Merge the data for current and previous week, ensuring all sales owners are included
    df = all_sales_owners_df.merge(df_current_agg, on="Sales Owner", how="left").merge(df_previous_agg, on="Sales Owner", how="left").fillna(0)

    # Calculate delta
    df["Delta"] = df["Current Week"] - df["Previous Week"]

    # Display the table with Streamlit
    st.dataframe(df, use_container_width=True)

# Streamlit app
def main():
    st.title("📊 Committed for the Month Data")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file:
        # Load the Excel file
        xls = pd.ExcelFile(uploaded_file)
        df_current = pd.read_excel(xls, sheet_name="Raw_Data")
        df_previous = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Preprocess data
        df_current = preprocess(df_current)
        df_previous = preprocess(df_previous)

        # Display the committed for the month table
        display_committed_for_month(df_current, df_previous)

if __name__ == "__main__":
    main()
