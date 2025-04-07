import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Sales Comparison", layout="wide")
st.title("📊 Weekly Sales Commitment vs Upside Comparison")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        # Load sheets
        xls = pd.ExcelFile(uploaded_file)
        current_week_df = pd.read_excel(xls, sheet_name="Raw_Data")
        previous_week_df = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Filter data
        current_committed = current_week_df[current_week_df["Status"] == "Committed for the Month"]
        previous_committed = previous_week_df[previous_week_df["Status"] == "Committed for the Month"]

        current_upside = current_week_df[current_week_df["Status"] == "Upsides for the Month"]
        previous_upside = previous_week_df[previous_week_df["Status"] == "Upsides for the Month"]

        # Group & convert to lakhs
        committed_current = current_committed.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        committed_previous = previous_committed.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        upside_current = current_upside.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        upside_previous = previous_upside.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        # Commitment Table
        commitment_df = pd.DataFrame({
            "Overall Committed (Current Week)": committed_current,
            "Overall Committed (Previous Week)": committed_previous
        }).fillna(0)
        commitment_df["Delta (Committed)"] = commitment_df["Overall Committed (Current Week)"] - commitment_df["Overall Committed (Previous Week)"]
        commitment_df = commitment_df.reset_index().astype({"Overall Committed (Current Week)": int, "Overall Committed (Previous Week)": int, "Delta (Committed)": int})

        # Upside Table
        upside_df = pd.DataFrame({
            "Overall Upside (Current Week)": upside_current,
            "Overall Upside (Previous Week)": upside_previous
        }).fillna(0)
        upside_df["Delta (Upside)"] = upside_df["Overall Upside (Current Week)"] - upside_df["Overall Upside (Previous Week)"]
        upside_df = upside_df.reset_index().astype({"Overall Upside (Current Week)": int, "Overall Upside (Previous Week)": int, "Delta (Upside)": int})

        # Side-by-side layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧾 Commitment Comparison (in ₹ Lakhs)")
            st.dataframe(commitment_df, use_container_width=True)

        with col2:
            st.subheader("🔁 Upside Comparison (in ₹ Lakhs)")
            st.dataframe(upside_df, use_container_width=True)

        # Optional export
        st.download_button("📥 Download Commitment CSV", commitment_df.to_csv(index=False).encode('utf-8'), file_name="commitment_comparison.csv", mime="text/csv")
        st.download_button("📥 Download Upside CSV", upside_df.to_csv(index=False).encode('utf-8'), file_name="upside_comparison.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
else:
    st.info("Upload your Excel file with sheets: 'Raw_Data' and 'PreviousWeek_Raw_Data'")
