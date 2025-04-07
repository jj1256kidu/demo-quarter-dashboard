import streamlit as st
import pandas as pd

# Function to preprocess the data
def preprocess(df):
    df["Quarter"] = df["Quarter"].astype(str).str.strip()
    df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df

# Function to filter data by status (Committed for the Month, Upside for the Month, etc.)
def filter_status(df, status):
    return df[df["Status"] == status]

# Function to aggregate the data
def agg_amount(df):
    return df.groupby("Sales Owner")["Amount"].sum().reset_index()

# Function to calculate and display metrics (Current Week Total, Previous Week Total, Delta)
def display_metrics(df_current, df_previous, status, label):
    # Filter the data based on status
    df_current_filtered = filter_status(df_current, status)
    df_previous_filtered = filter_status(df_previous, status)

    # Aggregate the data for current and previous week
    df_current_agg = agg_amount(df_current_filtered)
    df_previous_agg = agg_amount(df_previous_filtered)

    # Calculate total values for current and previous week
    total_current = df_current_agg["Amount"].sum() / 1e5
    total_previous = df_previous_agg["Amount"].sum() / 1e5
    delta = total_current - total_previous

    # Display the metrics for the selected status
    return total_current, total_previous, delta

# Function to display the table with Sales Owner and their data for each status (Committed, Upside, Closed Won, Overall Committed)
def display_data(df_current, df_previous, status, label):
    # Filter the data based on status
    df_current_filtered = filter_status(df_current, status)
    df_previous_filtered = filter_status(df_previous, status)

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

    # Divide by 10^5 and round the values to integers
    df["Current Week"] = (df["Current Week"] / 1e5).round(0).astype(int)
    df["Previous Week"] = (df["Previous Week"] / 1e5).round(0).astype(int)
    df["Delta"] = (df["Delta"] / 1e5).round(0).astype(int)

    # Apply custom CSS to reduce height and stretch the table, center-align, and remove width issues
    st.markdown("""
        <style>
            .stDataFrame {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: 20px;
            }
            .stTable {
                border-collapse: collapse;
                width: 100%;
                height: auto;
                margin: 0;
                padding: 0;
            }
            .stTable th, .stTable td {
                padding: 5px 12px;
                text-align: center;
                border: 1px solid #ddd;
                font-size: 12px;
                margin: 0;
            }
            .stTable th {
                background-color: #f2f2f2;
                font-size: 14px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Display the table with Streamlit (centered)
    st.dataframe(df.style.set_table_attributes('class="stTable"'), use_container_width=True)

# Streamlit app
def main():
    st.title("📊 Data Overview: Committed, Upside, Closed Won, and Overall Committed")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file:
        # Load the Excel file
        xls = pd.ExcelFile(uploaded_file)
        df_current = pd.read_excel(xls, sheet_name="Raw_Data")
        df_previous = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Preprocess data
        df_current = preprocess(df_current)
        df_previous = preprocess(df_previous)

        # Display KPIs for Committed, Upside, Closed Won, and Overall Committed
        st.markdown("### 📝 Key Metrics (KPI)")

        # Committed Data Metrics
        total_current_commit, total_previous_commit, delta_commit = display_metrics(df_current, df_previous, "Committed for the Month", "Committed Data")
        st.markdown(f"**Committed Data**: ₹ {total_current_commit:,.0f} Lakh (Current Week), ₹ {total_previous_commit:,.0f} Lakh (Previous Week), Δ ₹ {delta_commit:,.0f} Lakh")

        # Upside Data Metrics
        total_current_upside, total_previous_upside, delta_upside = display_metrics(df_current, df_previous, "Upside for the Month", "Upside Data")
        st.markdown(f"**Upside Data**: ₹ {total_current_upside:,.0f} Lakh (Current Week), ₹ {total_previous_upside:,.0f} Lakh (Previous Week), Δ ₹ {delta_upside:,.0f} Lakh")

        # Closed Won Data Metrics
        total_current_won, total_previous_won, delta_won = display_metrics(df_current, df_previous, "Closed Won", "Closed Won Data")
        st.markdown(f"**Closed Won Data**: ₹ {total_current_won:,.0f} Lakh (Current Week), ₹ {total_previous_won:,.0f} Lakh (Previous Week), Δ ₹ {delta_won:,.0f} Lakh")

        # Overall Committed Data Metrics (Committed + Closed Won)
        total_current_overall, total_previous_overall, delta_overall = display_metrics(df_current, df_previous, "Committed for the Month", "Overall Committed Data (Committed + Closed Won)")
        st.markdown(f"**Overall Committed Data**: ₹ {total_current_overall:,.0f} Lakh (Current Week), ₹ {total_previous_overall:,.0f} Lakh (Previous Week), Δ ₹ {delta_overall:,.0f} Lakh")

        # Display the tables for Committed Data
        display_data(df_current, df_previous, "Committed for the Month", "Committed Data")
        display_data(df_current, df_previous, "Upside for the Month", "Upside Data")
        display_data(df_current, df_previous, "Closed Won", "Closed Won Data")
        display_data(df_current, df_previous, "Committed for the Month", "Overall Committed Data (Committed + Closed Won)")

if __name__ == "__main__":
    main()
