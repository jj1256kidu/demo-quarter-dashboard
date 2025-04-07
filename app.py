import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel file", type=["xlsx"])

# Required column names
required_cols = {"Status", "Amount", "Quarter", "Sales Owner (Q1)"}

if uploaded_file:
    try:
        # Get all sheet names from the Excel file
        sheet_names = pd.ExcelFile(uploaded_file, engine='openpyxl').sheet_names

        # Allow user to select the two sheets
        col1, col2 = st.columns(2)
        with col1:
            current_sheet = st.selectbox("📅 Select CURRENT week sheet", sheet_names)
        with col2:
            previous_sheet = st.selectbox("📅 Select PREVIOUS week sheet", sheet_names)

        # Read selected sheets
        current_df = pd.read_excel(uploaded_file, sheet_name=current_sheet, engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name=previous_sheet, engine="openpyxl")

        # 🧼 Clean column names (strip leading/trailing whitespace)
        current_df.columns = current_df.columns.str.strip()
        previous_df.columns = previous_df.columns.str.strip()

        # Validate columns
        if not required_cols.issubset(set(current_df.columns)) or not required_cols.issubset(set(previous_df.columns)):
            missing_current = required_cols.difference(set(current_df.columns))
            missing_previous = required_cols.difference(set(previous_df.columns))
            st.error(f"❌ Missing columns:\n- Current Sheet: {', '.join(missing_current)}\n- Previous Sheet: {', '.join(missing_previous)}")
            st.stop()

        # Define Status values
        committed_type = "Committed for the month"
        upside_type = "Upside for the month"

        # Filter committed data
        current_committed_df = current_df[current_df['Status'].str.strip() == committed_type]
        previous_committed_df = previous_df[previous_df['Status'].str.strip() == committed_type]

        # Filter upside data
        current_upside_df = current_df[current_df['Status'].str.strip() == upside_type]
        previous_upside_df = previous_df[previous_df['Status'].str.strip() == upside_type]

        # Total committed & upside metrics
        current_committed = current_committed_df['Amount'].sum()
        previous_committed = previous_committed_df['Amount'].sum()
        delta_committed = current_committed - previous_committed

        current_upside = current_upside_df['Amount'].sum()
        previous_upside = previous_upside_df['Amount'].sum()
        delta_upside = current_upside - previous_upside

        # Show top-level metrics
        st.markdown("### 📈 Commitment Overview")
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.subheader("✅ Committed for the Month")
            st.metric(
                label="Current Total",
                value=f"₹{current_committed:,.0f}",
                delta=f"₹{delta_committed:,.0f}"
            )

        with mcol2:
            st.subheader("🔄 Upside for the Month")
            st.metric(
                label="Current Total",
                value=f"₹{current_upside:,.0f}",
                delta=f"₹{delta_upside:,.0f}"
            )

        # Sales Owner Summary Table (Committed only)
        current_committed_df['Sales Owner (Q1)'] = current_committed_df['Sales Owner (Q1)'].fillna("Unknown")
        previous_committed_df['Sales Owner (Q1)'] = previous_committed_df['Sales Owner (Q1)'].fillna("Unknown")

        # Group and merge
        current_grouped = current_committed_df.groupby('Sales Owner (Q1)')['Amount'].sum().reset_index()
        previous_grouped = previous_committed_df.groupby('Sales Owner (Q1)')['Amount'].sum().reset_index()

        merged = pd.merge(
            current_grouped,
            previous_grouped,
            on='Sales Owner (Q1)',
            how='outer',
            suffixes=('_Current Week', '_Previous Week')
        ).fillna(0)

        merged['Delta'] = merged['Amount_Current Week'] - merged['Amount_Previous Week']

        # Format and rename
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

        # Display the final summary table
        st.markdown("### 👤 Sales Owner Commitment Summary")
        st.dataframe(final_summary.style.format({
            'Overall Committed (Current Week)': '₹{:,.0f}',
            'Overall Committed (Previous Week)': '₹{:,.0f}',
            'Delta': '₹{:,.0f}'
        }))

    except Exception as e:
        st.error(f"❌ Error while processing the file: {e}")
else:
    st.info("📥 Please upload an Excel file with sheets containing Status, Amount, Quarter, and Sales Owner (Q1).")
