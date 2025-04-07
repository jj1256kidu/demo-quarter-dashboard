import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel file with 'Raw_Data' and 'PreviousWeek_Raw_Data' sheets", type=["xlsx"])

required_cols = {"Week", "Type", "Amount", "Quarter"}

if uploaded_file:
    try:
        # Read sheets
        current_df = pd.read_excel(uploaded_file, sheet_name="Raw_Data", engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name="PreviousWeek_Raw_Data", engine="openpyxl")

        # Validate columns
        if not required_cols.issubset(current_df.columns) or not required_cols.issubset(previous_df.columns):
            st.error(f"Both sheets must contain: {', '.join(required_cols)}")
            st.stop()

        # Extract week info
        current_week = current_df['Week'].iloc[0]
        previous_week = previous_df['Week'].iloc[0]
        st.markdown(f"**📅 Current Week:** `{current_week}` &nbsp;&nbsp;&nbsp; **📅 Previous Week:** `{previous_week}`")

        # ---------- 1. Committed for the month ----------
        committed_type = "Committed for the month"
        current_committed = current_df[current_df['Type'] == committed_type]['Amount'].sum()
        previous_committed = previous_df[previous_df['Type'] == committed_type]['Amount'].sum()
        delta_committed = current_committed - previous_committed

        # ---------- 2. Upside for the month ----------
        upside_type = "Upside for the month"
        current_upside = current_df[current_df['Type'] == upside_type]['Amount'].sum()
        previous_upside = previous_df[previous_df['Type'] == upside_type]['Amount'].sum()
        delta_upside = current_upside - previous_upside  # Optional

        # ---------- Display Layout ----------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Committed for the Month")
            st.metric(
                label="Current Week",
                value=f"₹{current_committed:,.0f}",
                delta=f"₹{delta_committed:,.0f}"
            )

        with col2:
            st.subheader("🔄 Upside for the Month")
            st.metric(
                label="Current Week",
                value=f"₹{current_upside:,.0f}",
                delta=f"₹{delta_upside:,.0f}"
            )

    except Exception as e:
        st.error(f"❌ Error while processing the file: {e}")
else:
    st.info("📥 Please upload a valid Excel file with sheets named 'Raw_Data' and 'PreviousWeek_Raw_Data'")
