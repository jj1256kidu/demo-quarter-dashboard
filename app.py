import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel file", type=["xlsx"])

required_cols = {"Status", "Amount", "Quarter", "Sales Owner (Q1)", "Function Overview Q1"}

def highlight_deltas(val):
    if isinstance(val, (int, float)) and val < 0:
        return 'color: red; font-weight: bold;'
    return ''

if uploaded_file:
    try:
        # Sheet selection
        sheet_names = pd.ExcelFile(uploaded_file, engine='openpyxl').sheet_names
        col1, col2 = st.columns(2)
        with col1:
            current_sheet = st.selectbox("📅 Select CURRENT week sheet", sheet_names)
        with col2:
            previous_sheet = st.selectbox("📅 Select PREVIOUS week sheet", sheet_names)

        # Load sheets
        current_df = pd.read_excel(uploaded_file, sheet_name=current_sheet, engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name=previous_sheet, engine="openpyxl")

        current_df.columns = current_df.columns.str.strip()
        previous_df.columns = previous_df.columns.str.strip()

        rename_map = {
            "Sales Owner (Q1)": "Sales Owner",
            "Function Overview Q1": "Practice"
        }
        current_df = current_df.rename(columns=rename_map)
        previous_df = previous_df.rename(columns=rename_map)

        expected_cols = {"Status", "Amount", "Quarter", "Sales Owner", "Practice"}
        if not expected_cols.issubset(set(current_df.columns)) or not expected_cols.issubset(set(previous_df.columns)):
            missing_current = expected_cols.difference(set(current_df.columns))
            missing_previous = expected_cols.difference(set(previous_df.columns))
            st.error(f"❌ Missing columns:\n- Current Sheet: {', '.join(missing_current)}\n- Previous Sheet: {', '.join(missing_previous)}")
            st.stop()

        # Filter Committed & Upside
        committed_type = "Committed for the month"
        upside_type = "Upside for the month"

        current_committed_df = current_df[current_df['Status'].str.strip() == committed_type]
        previous_committed_df = previous_df[previous_df['Status'].str.strip() == committed_type]

        current_upside_df = current_df[current_df['Status'].str.strip() == upside_type]
        previous_upside_df = previous_df[previous_df['Status'].str.strip() == upside_type]

        # Totals
        current_committed = current_committed_df['Amount'].sum()
        previous_committed = previous_committed_df['Amount'].sum()
        delta_committed = current_committed - previous_committed

        current_upside = current_upside_df['Amount'].sum()
        previous_upside = previous_upside_df['Amount'].sum()
        delta_upside = current_upside - previous_upside

        # Top-level Metrics
        st.markdown("### 📈 Commitment Overview")
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.subheader("✅ Committed for the Month")
            st.metric("Current Total", f"₹{current_committed:,.0f}", f"₹{delta_committed:,.0f}")
        with mcol2:
            st.subheader("🔄 Upside for the Month")
            st.metric("Current Total", f"₹{current_upside:,.0f}", f"₹{delta_upside:,.0f}")

        # --- SALES OWNER SUMMARY ---
        st.markdown("#### 🧾 Q1 SUMMARY – Sales Owner")
        current_committed_df['Sales Owner'] = current_committed_df['Sales Owner'].fillna("Unknown")
        previous_committed_df['Sales Owner'] = previous_committed_df['Sales Owner'].fillna("Unknown")

        current_grouped = current_committed_df.groupby('Sales Owner')['Amount'].sum().reset_index()
        previous_grouped = previous_committed_df.groupby('Sales Owner')['Amount'].sum().reset_index()

        merged = pd.merge(current_grouped, previous_grouped, on='Sales Owner', how='outer', suffixes=('_Current Week', '_Previous Week')).fillna(0)
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

        sales_final = pd.concat([merged, total_row], ignore_index=True)

        sales_styled = sales_final.style \
            .format({
                'Overall Committed (Current Week)': '₹{:,.0f}',
                'Overall Committed (Previous Week)': '₹{:,.0f}',
                'Delta': '₹{:,.0f}'
            }) \
            .map({'Delta': highlight_deltas}) \
            .apply(lambda df: ['background-color: yellow; font-weight: bold;' if i == len(df)-1 else '' for i in range(len(df))], axis=0)

        st.dataframe(sales_styled)

        # --- FUNCTION (PRACTICE) SUMMARY ---
        st.markdown("#### 🧾 Q1 SUMMARY – Function Overview")
        current_committed_df['Practice'] = current_committed_df['Practice'].fillna("Unknown")
        previous_committed_df['Practice'] = previous_committed_df['Practice'].fillna("Unknown")

        current_func = current_committed_df.groupby('Practice')['Amount'].sum().reset_index()
        previous_func = previous_committed_df.groupby('Practice')['Amount'].sum().reset_index()

        func_merged = pd.merge(current_func, previous_func, on='Practice', how='outer', suffixes=('_Current Week', '_Previous Week')).fillna(0)
        func_merged['Delta'] = func_merged['Amount_Current Week'] - func_merged['Amount_Previous Week']
        func_merged = func_merged.rename(columns={
            'Amount_Current Week': 'Overall Committed (Current Week)',
            'Amount_Previous Week': 'Overall Committed (Previous Week)'
        })

        func_total = pd.DataFrame({
            'Practice': ['Total'],
            'Overall Committed (Current Week)': [func_merged['Overall Committed (Current Week)'].sum()],
            'Overall Committed (Previous Week)': [func_merged['Overall Committed (Previous Week)'].sum()],
            'Delta': [func_merged['Delta'].sum()]
        })

        func_final = pd.concat([func_merged, func_total], ignore_index=True)

        func_styled = func_final.style \
            .format({
                'Overall Committed (Current Week)': '₹{:,.0f}',
                'Overall Committed (Previous Week)': '₹{:,.0f}',
                'Delta': '₹{:,.0f}'
            }) \
            .map({'Delta': highlight_deltas}) \
            .apply(lambda df: ['background-color: yellow; font-weight: bold;' if i == len(df)-1 else '' for i in range(len(df))], axis=0)

        st.dataframe(func_styled)

        # --- DOWNLOAD EXCEL ---
        st.markdown("### 📥 Download Summary Report")

        def to_excel(sales_df, func_df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                sales_df.to_excel(writer, index=False, sheet_name='Sales Summary')
                func_df.to_excel(writer, index=False, sheet_name='Function Summary')
            output.seek(0)
            return output

        excel_data = to_excel(sales_final, func_final)

        st.download_button(
            label="📤 Download Excel Report",
            data=excel_data,
            file_name="Quarter_Summary_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error while processing the file: {e}")
else:
    st.info("📥 Please upload an Excel file with required columns and select the sheets.")
