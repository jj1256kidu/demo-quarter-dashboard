import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel file with 'Raw_Data' and 'PreviousWeek_Raw_Data' sheets", type=["xlsx"])

required_cols = {"Week", "Type", "Amount", "Quarter"}

if uploaded_file:
    try:
        # Load Excel sheets
        current_df = pd.read_excel(uploaded_file, sheet_name="Raw_Data", engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name="PreviousWeek_Raw_Data", engine="openpyxl")

        # Validate essential columns
        if not required_cols.issubset(current_df.columns) or not required_cols.issubset(previous_df.columns):
            st.error(f"Missing required columns in one of the sheets: {', '.join(required_cols)}")
            st.stop()

        # Display week metadata
        current_week = current_df['Week'].iloc[0] if 'Week' in current_df.columns else 'N/A'
        previous_week = previous_df['Week'].iloc[0] if 'Week' in previous_df.columns else 'N/A'
        st.markdown(f"**📅 Current Week:** `{current_week}` &nbsp;&nbsp;&nbsp; **📅 Previous Week:** `{previous_week}`")

        # FILTER: Only include "Committed for the month" and "Upside for the month"
        committed_type = "Committed for the month"
        upside_type = "Upside for the month"

        current_committed_df = current_df[current_df['Type'] == committed_type]
        previous_committed_df = previous_df[previous_df['Type'] == committed_type]

        current_upside_df = current_df[current_df['Type'] == upside_type]
        previous_upside_df = previous_df[previous_df['Type'] == upside_type]

        # SUM: Total amount per type
        current_committed = current_committed_df['Amount'].sum()
        previous_committed = previous_committed_df['Amount'].sum()
        delta_committed = current_committed - previous_committed

        current_upside = current_upside_df['Amount'].sum()
        previous_upside = previous_upside_df['Amount'].sum()
        delta_upside = current_upside - previous_upside

        # DISPLAY
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Committed for the Month")
            st.metric(
                label="Current Week Total",
                value=f"₹{current_committed:,.0f}",
                delta=f"₹{delta_committed:,.0f}"
            )

        with col2:
            st.subheader("🔄 Upside for the Month")
            st.metric(
                label="Current Week Total",
                value=f"₹{current_upside:,.0f}",
                delta=f"₹{delta_upside:,.0f}"
            )

        # Optional: Expandable detail tables
        with st.expander("🔍 View Raw Committed Opportunities"):
            st.write("✅ Current Week - Committed")
            st.dataframe(current_committed_df)
            st.write("📅 Previous Week - Committed")
            st.dataframe(previous_committed_df)

        with st.expander("🔍 View Raw Upside Opportunities"):
            st.write("🔄 Current Week - Upside")
            st.dataframe(current_upside_df)
            st.write("📅 Previous Week - Upside")
            st.dataframe(previous_upside_df)

    except Exception as e:
        st.error(f"❌ Error processing the file: {e}")
else:
    st.info("📥 Please upload an Excel file with the correct sheets and required columns.")
