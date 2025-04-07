import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Commitment Comparison", layout="wide")

st.title("📊 Weekly Sales Commitment & Upside Comparison")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        current_week_df = pd.read_excel(xls, sheet_name="Raw_Data")
        previous_week_df = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Filter by Status
        current_committed = current_week_df[current_week_df["Status"] == "Committed for the Month"]
        previous_committed = previous_week_df[previous_week_df["Status"] == "Committed for the Month"]

        current_upside = current_week_df[current_week_df["Status"] == "Upsides for the Month"]
        previous_upside = previous_week_df[previous_week_df["Status"] == "Upsides for the Month"]

        # Group and sum Amounts in Lakhs
        committed_current = current_committed.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        committed_previous = previous_committed.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        upside_current = current_upside.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        upside_previous = previous_upside.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        # Merge all
        comparison_df = pd.DataFrame({
            "Overall Committed (Current Week)": committed_current,
            "Overall Committed (Previous Week)": committed_previous,
            "Overall Upside (Current Week)": upside_current,
            "Overall Upside (Previous Week)": upside_previous
        }).fillna(0)

        # Calculate Deltas
        comparison_df["Delta (Committed)"] = (
            comparison_df["Overall Committed (Current Week)"] -
            comparison_df["Overall Committed (Previous Week)"]
        ).astype(int)

        comparison_df["Delta (Upside)"] = (
            comparison_df["Overall Upside (Current Week)"] -
            comparison_df["Overall Upside (Previous Week)"]
        ).astype(int)

        comparison_df = comparison_df.reset_index()

        # Ensure all values are int
        for col in comparison_df.columns[1:]:
            comparison_df[col] = comparison_df[col].astype(int)

        st.subheader("🧾 Commitment & Upside Comparison Table (in ₹ Lakhs)")
        st.dataframe(comparison_df, use_container_width=True)

        # Optional CSV export
        csv = comparison_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name="commitment_upside_comparison.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("Upload an Excel file with sheets: 'Raw_Data' & 'PreviousWeek_Raw_Data'")
