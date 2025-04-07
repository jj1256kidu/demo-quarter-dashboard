import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Sales Comparison", layout="wide")
st.title("📊 Weekly Sales Comparison: Commitment & Upside")

uploaded_file = st.file_uploader("📂 Upload Excel File", type="xlsx")

if uploaded_file:
    try:
        # Load Excel
        xls = pd.ExcelFile(uploaded_file)
        current_week_df = pd.read_excel(xls, sheet_name="Raw_Data")
        previous_week_df = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Ensure 'Quarter' exists
        if "Quarter" not in current_week_df.columns or "Quarter" not in previous_week_df.columns:
            st.error("❌ 'Quarter' column not found in one of the sheets.")
            st.stop()

        # ---- Filters ----
        all_quarters = sorted(current_week_df["Quarter"].dropna().unique())
        all_sales_owners = sorted(current_week_df["Sales Owner"].dropna().unique())

        selected_quarter = st.selectbox("📅 Select Quarter", options=["All"] + all_quarters)
        selected_owner = st.selectbox("👤 Select Sales Owner", options=["All"] + all_sales_owners)

        # Apply filters
        def apply_filters(df):
            if selected_quarter != "All":
                df = df[df["Quarter"] == selected_quarter]
            if selected_owner != "All":
                df = df[df["Sales Owner"] == selected_owner]
            return df

        current_week_df = apply_filters(current_week_df)
        previous_week_df = apply_filters(previous_week_df)

        # ---- COMMITMENT ----
        committed_current = current_week_df[current_week_df["Status"] == "Committed for the Month"]
        committed_previous = previous_week_df[previous_week_df["Status"] == "Committed for the Month"]

        committed_current_grouped = committed_current.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        committed_previous_grouped = committed_previous.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        commitment_df = pd.DataFrame({
            "Overall Committed (Current Week)": committed_current_grouped,
            "Overall Committed (Previous Week)": committed_previous_grouped
        }).fillna(0)

        commitment_df["Delta (Committed)"] = commitment_df["Overall Committed (Current Week)"] - commitment_df["Overall Committed (Previous Week)"]
        commitment_df = commitment_df.reset_index().astype(int)

        # ---- UPSIDE ----
        upside_current = current_week_df[current_week_df["Status"] == "Upside for the Month"]
        upside_previous = previous_week_df[previous_week_df["Status"] == "Upside for the Month"]

        upside_current_grouped = upside_current.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
        upside_previous_grouped = upside_previous.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

        upside_df = pd.DataFrame({
            "Overall Upside (Current Week)": upside_current_grouped,
            "Overall Upside (Previous Week)": upside_previous_grouped
        }).fillna(0)

        upside_df["Delta (Upside)"] = upside_df["Overall Upside (Current Week)"] - upside_df["Overall Upside (Previous Week)"]
        upside_df = upside_df.reset_index().astype(int)

        # ---- DISPLAY ----
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧾 Commitment Comparison (in ₹ Lakhs)")
            st.dataframe(commitment_df, use_container_width=True)

        with col2:
            st.subheader("🔁 Upside Comparison (in ₹ Lakhs)")
            st.dataframe(upside_df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")
else:
    st.info("Upload an Excel file with sheets: `Raw_Data` and `PreviousWeek_Raw_Data` containing 'Sales Owner', 'Status', 'Amount', and 'Quarter'.")
