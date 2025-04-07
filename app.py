import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel file", type=["xlsx"])

required_cols = {"Status", "Amount", "Quarter", "Sales Owner (Q1)", "Function Overview Q1"}

if uploaded_file:
    try:
        # Load sheet names
        sheet_names = pd.ExcelFile(uploaded_file, engine='openpyxl').sheet_names

        # Sheet selectors
        col1, col2 = st.columns(2)
        with col1:
            current_sheet = st.selectbox("📅 Select CURRENT week sheet", sheet_names)
        with col2:
            previous_sheet = st.selectbox("📅 Select PREVIOUS week sheet", sheet_names)

        # Load selected sheets
        current_df = pd.read_excel(uploaded_file, sheet_name=current_sheet, engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name=previous_sheet, engine="openpyxl")

        # Clean column names
        current_df.columns = current_df.columns.str.strip()
        previous_df.columns = previous_df.columns.str.strip()

        # Rename columns to expected internal names
        column_mapping = {
            "Sales Owner (Q1)": "Sales Owner",
            "Function Overview Q1": "Practice"
        }
        current_df = current_df.rename(columns=column_mapping)
        previous_df = previous_df.rename(columns=column_mapping)

        # Validate columns after rename
        expected_cols = {"Status", "Amount", "Quarter", "Sales Owner", "Practice"}
        if not expected_cols.issubset(set(current_df.columns)) or not expected_cols.issubset(set(previous_df.columns)):
            missing_current = expected_cols.difference(set(current_df.columns))
            missing_previous = expected_cols.difference(set(previous_df.columns))
            st.error(f"❌ Missing columns:\n- Current Sheet: {', '.join(missing_current)}\n- Previous Sheet: {', '.join(missing_previous)}")
            st.stop()

        # Define types
        committed_type = "Committed for the month"
        upside_type = "Upside for the month"

        # Filter by status
        current_committed_df = current_df[current_df['Status'].str.strip() == committed_type]
        previous_committed_df = previous_df[previous_df['Status'].str.strip() == committed_type]

        current_upside_df = current_df[current_df['Status'].str.strip() == upside_type]
        previous_upside_df = previous_df[previous_df['Status'].str.strip() == upside_type]

        # Metrics
        current_committed = current_committed_df['Amount'].sum()
        previous_committed = previous_committed_df['Amount'].sum()
        delta_committed = current_committed - previous_committed

        current_upside = current_upside_df['Amount'].sum()
        previous_upside = previous_upside_df['Amount'].sum()
        delta_upside = current_upside - previous_upside

        # Display Top-Level Metrics
        st.markdown("### 📈 Commitment Overview")
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.subheader("✅ Committed for the Month")
            st.metric("Current Total", f"₹{current_committed:,.0f}", f"₹{delta_committed:,.0f}")
        with mcol2:
            st.subheader("🔄 Upside for the Month")
            st.metric("Current Total", f"₹{current_upside:,.0f}", f"₹{delta_upside:,.0f}")

        # ------------------------
        # Sales Owner Summary
        # ------------------------
        st.markdown("### 👤 Sales Owner Commitment Summary")

        current_committed_df['Sales Owner'] = current_committed_df['Sales Owner'].fillna("Unknown")
        previous_committed_df['Sales Owner'] = previous_committed_df['Sales Owner'].fillna("Unknown")

        current_grouped = current_committed_df.groupby('Sales Owner')['Amount'].sum().reset_index()
        previous_grouped = previous_committed_df.groupby('Sales Owner')['Amount'].sum().reset_index()

        merged = pd.merge(
            current_grouped, previous_grouped,
            on='Sales Owner', how='outer',
            suffixes=('_Current Week', '_Previous Week')
        ).fillna(0)

        merged['Delta'] = merged['Amount_Current Week'] - merged['Amount_Previous Week']
        merged = merged.rename(columns={
            'Amount_Current Week': 'Overall Committed (Current Week)',
            'Amount_Previous Week': 'Overall Committed (Previous Week)'
        })

        total_row = pd.DataFrame({
            'Sales Owner': ['Total'],
            'Overall Committed (Current Week)': [merged['Overall Committed (Current Week)'].sum()],
            'Overall Committed (Previous Week)': [merged['Overall Committed (Previous Week)'].sum()],
            'Delta': [merged['Delta'].sum()]
        })

        final_summary = pd.concat([merged, total_row], ignore_index=True)

        def highlight_deltas(val):
            if isinstance(val, (int, float)) and val < 0:
                return 'color: red; font-weight: bold;'
            return ''

        st.dataframe(final_summary.style.format({
            'Overall Committed (Current Week)': '₹{:,.0f}',
            'Overall Committed (Previous Week)': '₹{:,.0f}',
            'Delta': '₹{:,.0f}'
        }).applymap(highlight_deltas, subset=['Delta']))

        # -----------------------------
        # Practice (Function Overview Q1) Summary
        # -----------------------------
        st.markdown("### 🧩 Function Overview Commitment Summary")

        current_committed_df['Practice'] = current_committed_df['Practice'].fillna("Unknown")
        previous_committed_df['Practice'] = previous_committed_df['Practice'].fillna("Unknown")

        current_func_grouped = current_committed_df.groupby('Practice')['Amount'].sum().reset_index()
        previous_func_grouped = previous_committed_df.groupby('Practice')['Amount'].sum().reset_index()

        func_merged = pd.merge(
            current_func_grouped, previous_func_grouped,
            on='Practice', how='outer',
            suffixes=('_Current Week', '_Previous Week')
        ).fillna(0)

        func_merged['Delta'] = func_merged['Amount_Current Week'] - func_merged['Amount_Previous Week']
        func_merged = func_merged.rename(columns={
            'Amount_Current Week': 'Overall Committed (Current Week)',
            'Amount_Previous Week': 'Overall Committed (Previous Week)'
        })

        func_total_row = pd.DataFrame({
            'Practice': ['Total'],
            'Overall Committed (Current Week)': [func_merged['Overall Committed (Current Week)'].sum()],
            'Overall Committed (Previous Week)': [func_merged['Overall Committed (Previous Week)'].sum()],
            'Delta': [func_merged['Delta'].sum()]
        })

        func_final = pd.concat([func_merged, func_total_row], ignore_index=True)

        st.dataframe(func_final.style.format({
            'Overall Committed (Current Week)': '₹{:,.0f}',
            'Overall Committed (Previous Week)': '₹{:,.0f}',
            'Delta': '₹{:,.0f}'
        }).applymap(highlight_deltas, subset=['Delta']))

    except Exception as e:
        st.error(f"❌ Error while processing the file: {e}")
else:
    st.info("📥 Please upload an Excel file with the required columns and select the sheets to compare.")
