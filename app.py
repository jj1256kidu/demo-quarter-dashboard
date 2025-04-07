import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Commitment Comparison", layout="centered")

st.title("📊 Weekly Sales Commitment Comparison")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        # Load both sheets
        xls = pd.ExcelFile(uploaded_file)
        current_week_df = pd.read_excel(xls, sheet_name="Raw_Data")
        previous_week_df = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Filter for committed deals
        current_committed = current_week_df[current_week_df["Status"] == "Committed for the Month"]
        previous_committed = previous_week_df[previous_week_df["Status"] == "Committed for the Month"]

        # Group by Sales Owner and sum Amount in Lakhs (₹10^5), rounded
        current_grouped = current_committed.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        previous_grouped = previous_committed.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        # Merge both DataFrames
        comparison_df = pd.DataFrame({
            "Overall Committed (Current Week)": current_grouped,
            "Overall Committed (Previous Week)": previous_grouped
        }).fillna(0)

        comparison_df["Delta"] = comparison_df["Overall Committed (Current Week)"] - comparison_df["Overall Committed (Previous Week)"]
        comparison_df = comparison_df.reset_index()
        comparison_df = comparison_df.astype({
            "Overall Committed (Current Week)": "int",
            "Overall Committed (Previous Week)": "int",
            "Delta": "int"
        })

        st.subheader("🧾 Commitment Comparison Table (in ₹ Lakhs)")
        st.dataframe(comparison_df, use_container_width=True)

        # Optional: Download as CSV
        csv = comparison_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download as CSV", data=csv, file_name="weekly_comparison.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    st.info("Please upload an Excel file containing 'Raw_Data' and 'PreviousWeek_Raw_Data' sheets.")
