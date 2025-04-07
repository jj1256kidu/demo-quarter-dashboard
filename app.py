
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Initialize session state to store uploaded file and sheet names
if "excel_data" not in st.session_state:
    st.session_state.excel_data = None
if "sheet_names" not in st.session_state:
    st.session_state.sheet_names = []

# Define pages
page = st.sidebar.selectbox("Select Page", ["📁 Data Input", "📊 Quarter Summary Dashboard"])

# Page 1: Data Input
if page == "📁 Data Input":
    st.title("📊 Weekly Commitment Comparison Tool")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            st.session_state.excel_data = xls
            st.session_state.sheet_names = xls.sheet_names
            st.success("✅ Excel file loaded successfully!")
        except Exception as e:
            st.error(f"⚠️ Error reading file: {e}")

    if st.session_state.excel_data:
        current_week_sheet = st.selectbox("Select Current Week Sheet", st.session_state.sheet_names, key="current")
        previous_week_sheet = st.selectbox("Select Previous Week Sheet", st.session_state.sheet_names, key="previous")

# Page 2: Dashboard
if page == "📊 Quarter Summary Dashboard":
    st.title("📈 Quarter Summary Dashboard")

    if not st.session_state.excel_data:
        st.warning("Please upload an Excel file in the Data Input page.")
    else:
        xls = st.session_state.excel_data
        try:
            current_data = pd.read_excel(xls, sheet_name=st.session_state.current)
            previous_data = pd.read_excel(xls, sheet_name=st.session_state.previous)

            # Remove rows with empty Sales Owner
            current_data = current_data[current_data['Sales Owner'].notna()]
            previous_data = previous_data[previous_data['Sales Owner'].notna()]

            quarters = sorted(current_data['Quarter'].dropna().unique().tolist())
            selected_quarter = st.selectbox("Select Quarter", quarters)

            sales_owners = sorted(set(current_data['Sales Owner']) | set(previous_data['Sales Owner']))
            selected_owner = st.selectbox("Select Sales Owner", ["All"] + sales_owners)

            # Filter by Quarter and Sales Owner
            def filter_df(df):
                df = df[df['Quarter'] == selected_quarter]
                if selected_owner != "All":
                    df = df[df['Sales Owner'] == selected_owner]
                return df

            current_filtered = filter_df(current_data)
            previous_filtered = filter_df(previous_data)

            # Calculate Committed and Upside Comparisons
            def summarize(df, status_value):
                df_filtered = df[df['Status'] == status_value]
                return df_filtered.groupby('Sales Owner')['Amount'].sum().div(1e5).round().astype(int).reset_index()

            committed_current = summarize(current_filtered, "Committed for the Month")
            committed_previous = summarize(previous_filtered, "Committed for the Month")
            committed = pd.merge(committed_current, committed_previous, on='Sales Owner', how='outer', suffixes=(" (Current Week)", " (Previous Week)")).fillna(0)
            committed["∆ Committed"] = committed["Amount (Current Week)"] - committed["Amount (Previous Week)"]

            upside_current = summarize(current_filtered, "Upside for the Month")
            upside_previous = summarize(previous_filtered, "Upside for the Month")
            upside = pd.merge(upside_current, upside_previous, on='Sales Owner', how='outer', suffixes=(" (Current Week)", " (Previous Week)")).fillna(0)
            upside["∆ Upside"] = upside["Amount (Current Week)"] - upside["Amount (Previous Week)"]

            # Add S. No and Total row
            def finalize_table(df, label):
                df.insert(0, "S. No.", range(1, len(df) + 1))
                totals = ["📊 Total", *["" for _ in range(len(df.columns) - 2)]]
                sum_row = df.iloc[:, 2:].sum().astype(int)
                total_row = pd.DataFrame([["", "📊 Total", *sum_row]], columns=df.columns)
                df = pd.concat([df, total_row], ignore_index=True)
                return df

            committed = finalize_table(committed, "Committed")
            upside = finalize_table(upside, "Upside")

            # Display side-by-side tables
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("📄 **Commitment Comparison (in ₹ Lakhs)**")
                st.dataframe(committed, use_container_width=True)
            with col2:
                st.markdown("🔁 **Upside Comparison (in ₹ Lakhs)**")
                st.dataframe(upside, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Error processing data: {e}")
