import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

uploaded_file = st.file_uploader("📄 Upload Excel file", type=["xlsx"])

required_cols = {"Status", "Amount", "Quarter", "Sales Owner (Q1)", "Function Overview Q1"}

def highlight_deltas(val):
    if isinstance(val, (int, float)) and val < 0:
        return 'color: red; font-weight: bold;'
    return ''

def highlight_total_rows(df):
    def style_row(row):
        if row.name == len(df) - 1:
            return ['background-color: yellow; font-weight: bold;'] * len(row)
        return [''] * len(row)
    return style_row

if uploaded_file:
    try:
        # Load fixed sheet names
        current_df = pd.read_excel(uploaded_file, sheet_name="Raw_Data", engine="openpyxl")
        previous_df = pd.read_excel(uploaded_file, sheet_name="PreviousWeek_Raw_Data", engine="openpyxl")

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

        committed_type = "Committed for the month"

        current_committed_df = current_df[current_df['Status'].str.strip() == committed_type]
        previous_committed_df = previous_df[previous_df['Status'].str.strip() == committed_type]

        current_committed_df['Sales Owner'] = current_committed_df['Sales Owner'].fillna("Unknown")
        previous_committed_df['Sales Owner'] = previous_committed_df['Sales Owner'].fillna("Unknown")
        current_committed_df['Practice'] = current_committed_df['Practice'].fillna("Unknown")
        previous_committed_df['Practice'] = previous_committed_df['Practice'].fillna("Unknown")

        # Totals for top-level metrics
        current_total = current_committed_df['Amount'].sum()
        previous_total = previous_committed_df['Amount'].sum()
        delta_total = current_total - previous_total
        achievement_pct = (current_total / previous_total * 100) if previous_total != 0 else 0

        st.markdown("""
### 🧾 Q1 SUMMARY — Committed & Upside for the Month  
This section compares the **Committed** data from:
- ✅ `Raw_Data` (Current Week)
- 📁 `PreviousWeek_Raw_Data` (Previous Week)

**🟨 Yellow Row** = Total  
**🔴 Red Text** = Negative change
""")
        mcol1, mcol2, mcol3 = st.columns([2, 2, 1])
        with mcol1:
            st.metric("Overall Committed (Current Week)", f"₹{current_total:,.0f}")
        with mcol2:
            st.metric("Overall Committed (Previous Week)", f"₹{previous_total:,.0f}", f"₹{delta_total:,.0f}")
        with mcol3:
            st.metric("Achievement %", f"{achievement_pct:.0f}%")

        # --- SALES OWNER SUMMARY ---
        st.markdown("#### 👤 Sales Owner (Q1) — Weekly Comparison")
        sales_grouped = pd.merge(
            current_committed_df.groupby("Sales Owner")["Amount"].sum().reset_index().rename(columns={"Amount": "Current Week"}),
            previous_committed_df.groupby("Sales Owner")["Amount"].sum().reset_index().rename(columns={"Amount": "Previous Week"}),
            on="Sales Owner",
            how="outer"
        ).fillna(0)
        sales_grouped["Delta"] = sales_grouped["Current Week"] - sales_grouped["Previous Week"]
        total_row = pd.DataFrame({
            "Sales Owner": ["Total"],
            "Current Week": [sales_grouped["Current Week"].sum()],
            "Previous Week": [sales_grouped["Previous Week"].sum()],
            "Delta": [sales_grouped["Delta"].sum()]
        })
        sales_final = pd.concat([sales_grouped, total_row], ignore_index=True)
        st.dataframe(
            sales_final.style
                .format({"Current Week": "₹{:,.0f}", "Previous Week": "₹{:,.0f}", "Delta": "₹{:,.0f}"})
                .map({"Delta": highlight_deltas})
                .apply(highlight_total_rows(sales_final), axis=1)
        )

        # --- FUNCTION OVERVIEW SUMMARY ---
        st.markdown("#### 🏢 Function Overview (Practice) — Weekly Comparison")
        func_grouped = pd.merge(
            current_committed_df.groupby("Practice")["Amount"].sum().reset_index().rename(columns={"Amount": "Current Week"}),
            previous_committed_df.groupby("Practice")["Amount"].sum().reset_index().rename(columns={"Amount": "Previous Week"}),
            on="Practice",
            how="outer"
        ).fillna(0)
        func_grouped["Delta"] = func_grouped["Current Week"] - func_grouped["Previous Week"]
        func_total = pd.DataFrame({
            "Practice": ["Total"],
            "Current Week": [func_grouped["Current Week"].sum()],
            "Previous Week": [func_grouped["Previous Week"].sum()],
            "Delta": [func_grouped["Delta"].sum()]
        })
        func_final = pd.concat([func_grouped, func_total], ignore_index=True)
        st.dataframe(
            func_final.style
                .format({"Current Week": "₹{:,.0f}", "Previous Week": "₹{:,.0f}", "Delta": "₹{:,.0f}"})
                .map({"Delta": highlight_deltas})
                .apply(highlight_total_rows(func_final), axis=1)
        )

        # --- DOWNLOAD ---
        st.markdown("### 📅 Download Summary Report")

        def to_excel(sales_df, func_df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                sales_df.to_excel(writer, index=False, sheet_name='Sales Summary')
                func_df.to_excel(writer, index=False, sheet_name='Function Summary')
            output.seek(0)
            return output

        excel_data = to_excel(sales_final, func_final)

        st.download_button(
            label="📄 Download Excel Report",
            data=excel_data,
            file_name="Quarter_Summary_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error while processing the file: {e}")
else:
    st.info("📅 Please upload an Excel file with sheets 'Raw_Data' and 'PreviousWeek_Raw_Data'.")
