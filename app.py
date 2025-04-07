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

    # Apply color coding for delta
    delta_color = "green" if delta > 0 else "red" if delta < 0 else "black"

    # Return the total values and delta color
    return total_current, total_previous, delta, delta_color

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

        # Display KPIs with custom styles
        st.markdown("### 📝 Key Metrics (KPI)")
        st.markdown("---")  # Horizontal line for separation

        # Committed Data Metrics
        total_current_commit, total_previous_commit, delta_commit, delta_commit_color = display_metrics(df_current, df_previous, "Committed for the Month", "Committed Data")
        st.markdown(f"**Committed Data**: <span style='font-size:20px; color: {delta_commit_color};'>₹ {total_current_commit:,.0f} Lakh</span> (Current Week), <span style='font-size:20px;'>₹ {total_previous_commit:,.0f} Lakh</span> (Previous Week), <span style='font-size:20px; color: {delta_commit_color};'>Δ ₹ {delta_commit:,.0f} Lakh</span>", unsafe_allow_html=True)

        # Upside Data Metrics
        total_current_upside, total_previous_upside, delta_upside, delta_upside_color = display_metrics(df_current, df_previous, "Upside for the Month", "Upside Data")
        st.markdown(f"**Upside Data**: <span style='font-size:20px; color: {delta_upside_color};'>₹ {total_current_upside:,.0f} Lakh</span> (Current Week), <span style='font-size:20px;'>₹ {total_previous_upside:,.0f} Lakh</span> (Previous Week), <span style='font-size:20px; color: {delta_upside_color};'>Δ ₹ {delta_upside:,.0f} Lakh</span>", unsafe_allow_html=True)

        # Closed Won Data Metrics
        total_current_won, total_previous_won, delta_won, delta_won_color = display_metrics(df_current, df_previous, "Closed Won", "Closed Won Data")
        st.markdown(f"**Closed Won Data**: <span style='font-size:20px; color: {delta_won_color};'>₹ {total_current_won:,.0f} Lakh</span> (Current Week), <span style='font-size:20px;'>₹ {total_previous_won:,.0f} Lakh</span> (Previous Week), <span style='font-size:20px; color: {delta_won_color};'>Δ ₹ {delta_won:,.0f} Lakh</span>", unsafe_allow_html=True)

        # Overall Committed Data Metrics (Committed + Closed Won)
        total_current_overall, total_previous_overall, delta_overall, delta_overall_color = display_metrics(df_current, df_previous, "Committed for the Month", "Overall Committed Data (Committed + Closed Won)")
        st.markdown(f"**Overall Committed Data**: <span style='font-size:20px; color: {delta_overall_color};'>₹ {total_current_overall:,.0f} Lakh</span> (Current Week), <span style='font-size:20px;'>₹ {total_previous_overall:,.0f} Lakh</span> (Previous Week), <span style='font-size:20px; color: {delta_overall_color};'>Δ ₹ {delta_overall:,.0f} Lakh</span>", unsafe_allow_html=True)

        st.markdown("---")  # Horizontal line for separation

        # Display the tables for Committed Data
        display_data(df_current, df_previous, "Committed for the Month", "Committed Data")
        display_data(df_current, df_previous, "Upside for the Month", "Upside Data")
        display_data(df_current, df_previous, "Closed Won", "Closed Won Data")
        display_data(df_current, df_previous, "Committed for the Month", "Overall Committed Data (Committed + Closed Won)")

if __name__ == "__main__":
    main()
