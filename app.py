import streamlit as st
import pandas as pd

st.set_page_config(page_title="🧾 Sales Weekly Comparison", layout="wide")
st.markdown("## 🗓️ Weekly Sales Commitment & Upside Tracker")

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        current_week_df = pd.read_excel(xls, sheet_name="Raw_Data")
        previous_week_df = pd.read_excel(xls, sheet_name="PreviousWeek_Raw_Data")

        # Basic validation
        required_cols = ['Quarter', 'Sales Owner', 'Status', 'Amount']
        for col in required_cols:
            if col not in current_week_df.columns or col not in previous_week_df.columns:
                st.error(f"🚨 Missing column: `{col}` in one of the sheets.")
                st.stop()

        # Filters
        colA, colB = st.columns([1, 1])
        with colA:
            quarters = sorted(current_week_df["Quarter"].dropna().unique())
            selected_quarter = st.selectbox("📅 Select Quarter", options=["All"] + quarters)
        with colB:
            sales_owners = sorted(current_week_df["Sales Owner"].dropna().unique())
            selected_owner = st.selectbox("👤 Select Sales Owner", options=["All"] + sales_owners)

        # Filtering Function
        def filter_data(df):
            if selected_quarter != "All":
                df = df[df["Quarter"] == selected_quarter]
            if selected_owner != "All":
                df = df[df["Sales Owner"] == selected_owner]
            return df

        current_week_df = filter_data(current_week_df)
        previous_week_df = filter_data(previous_week_df)

        # --- Helper for Commit/Upside ---
        def generate_summary(status_filter, label):
            current_filtered = current_week_df[current_week_df["Status"] == status_filter]
            previous_filtered = previous_week_df[previous_week_df["Status"] == status_filter]

            current_sum = current_filtered.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
            previous_sum = previous_filtered.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

            df_summary = pd.DataFrame({
                f"{label} (Current Week)": current_sum,
                f"{label} (Previous Week)": previous_sum
            }).fillna(0)

            df_summary[f"Δ {label}"] = df_summary[f"{label} (Current Week)"] - df_summary[f"{label} (Previous Week)"]
            df_summary = df_summary.reset_index()
            for col in df_summary.columns[1:]:
                df_summary[col] = df_summary[col].astype(int)
            return df_summary

        commitment_df = generate_summary("Committed for the Month", "Committed")
        upside_df = generate_summary("Upside for the Month", "Upside")

        # --- Display Both Tables ---
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧾 Commitment Comparison (in ₹ Lakhs)")
            st.dataframe(commitment_df.style.format({
                "Committed (Current Week)": "{:,}",
                "Committed (Previous Week)": "{:,}",
                "Δ Committed": "{:+,}"
            }), use_container_width=True)

        with col2:
            st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
            st.dataframe(upside_df.style.format({
                "Upside (Current Week)": "{:,}",
                "Upside (Previous Week)": "{:,}",
                "Δ Upside": "{:+,}"
            }), use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("📌 Please upload an Excel file containing `Raw_Data` and `PreviousWeek_Raw_Data` sheets with the correct columns.")
