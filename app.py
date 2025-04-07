import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel file with 'Raw_Data' and 'PreviousWeek_Raw_Data' sheets", type=["xlsx"])

# Required columns for validation
required_cols = {"Status", "Amount", "Quarter", "Sales Owner (Q1)"}

if uploaded_file:
    try:
        # Load sheets
        current_df = pd.read_excel(uploaded_file, sheet_name="Raw_Data", engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name="PreviousWeek_Raw_Data", engine="openpyxl")

        # Validate column presence
        if not required_cols.issubset(current_df.columns) or not required_cols.issubset(previous_df.columns):
            st.error(f"Missing required columns in one or both sheets: {', '.join(required_cols)}")
            st.stop()

        # Define status types
        committed_type = "Committed for the month"
        upside_type = "Upside for the month"

        # Filter Committed
        current_committed_df = current_df[current_df['Status'] == committed_type]
        previous_committed_df = previous_df[previous_df['Status'] == committed_type]

        # Filter Upside
        current_upside_df = current_df[current_df['Status'] == upside_type]
        previous_upside_df = previous_df[previous_df['Status'] == upside_type]

        # ---- TOTAL METRICS ----
        current_committed = current_committed_df['Amount'].sum()
        previous_committed = previous_committed_df['Amount'].sum()
        delta_committed = current_committed - previous_committed

        current_upside = current_upside_df['Amount'].sum()
        previous_upside = previous_upside_df['Amount'].sum()
        delta_upside = current_upside - previous_upside

        # ---- METRIC DISPLAY ----
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Committed for the Month")
            st.metric(
                label="Current Total",
                value=f"₹{current_committed:,.0f}",
                delta=f"₹{delta_committed:,.0f}"
            )

        with col2:
            st.subheader("🔄 Upside for the Month")
            st.metric(
                label="Current Total",
                value=f"₹{current_upside:,.0f}",
                delta=f"₹{delta_upside:,.0f}"
            )

        # ---- SALES OWNER TABLE ----
        # Fill NAs just in case
        current_committed_df['Sales Owner (Q1)'] = current_committed_df['Sales Owner (Q1)'].fillna("Unknown")
        previous_committed_df['Sales Owner (Q1)'] = previous_committed_df['Sales Owner (Q1)'].fillna("Unknown")

        # Group by Sales Owner
        current_grouped = current_committed_df.groupby('Sales Owner (Q1)')['Amount'].sum().reset_index()
        previous_grouped = previous_committed_df.groupby('Sales Owner (Q1)')['Amount'].sum().reset_index()

        # Merge and calculate delta
        merged = pd.merge(
            current_grouped,
            previous_grouped,
            on='Sales Owner (Q1)',
            how='outer',
            suffixes=('_Current Week', '_Previous Week')
        ).fillna(0)

        merged['Delta'] = merged['Amount_Current Week'] - merged['Amount_Previous Week']

        # Rename for display
        merged = merged.rename(columns={
            'Sales Owner (Q1)': 'Sales Owner',
            'Amount_Current Week': 'Overall Committed (Current Week)',
            'Amount_Previous Week': 'Overall Committed (Previous Week)'
        })

        # Add total row
        total_row = pd.DataFrame({
            'Sales Owner': ['Total'],
            'Overall Committed (Current Week)': [merged['Overall Committed (Current Week)'].sum()],
            'Overall Committed (Previous Week)': [merged['Overall Committed (Previous Week)'].sum()],
            'Delta': [merged['Delta'].sum()]
        })

        final_summary = pd.concat([merged, total_row], ignore_index=True)

        # Show sales summary table
        st.markdown("### 👤 Sales Owner Commitment Summary")
        st.dataframe(final_summary.style.format({
            'Overall Committed (Current Week)': '₹{:,.0f}',
            'Overall Committed (Previous Week)': '₹{:,.0f}',
            'Delta': '₹{:,.0f}'
        }))

    except Exception as e:
        st.error(f"❌ Error while processing the file: {e}")
else:
    st.info("📥 Upload an Excel file with sheets 'Raw_Data' and 'PreviousWeek_Raw_Data'")
