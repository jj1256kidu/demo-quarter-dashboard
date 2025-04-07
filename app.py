
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Weekly Commitment Comparison Tool")

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'current_week_df' not in st.session_state:
    st.session_state.current_week_df = pd.DataFrame()
if 'previous_week_df' not in st.session_state:
    st.session_state.previous_week_df = pd.DataFrame()
if 'current_sheet' not in st.session_state:
    st.session_state.current_sheet = None
if 'previous_sheet' not in st.session_state:
    st.session_state.previous_sheet = None

# Sidebar navigation
page = st.sidebar.radio("Go to", ["📂 Data Input", "📊 Quarter Summary Dashboard"])

if page == "📂 Data Input":
    st.title("📊 Weekly Commitment Comparison Tool")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        xl = pd.ExcelFile(uploaded_file)
        st.success("✅ Excel file loaded successfully!")
        sheet_names = xl.sheet_names

        current_sheet = st.selectbox("Select Current Week Sheet", sheet_names, key="cur")
        previous_sheet = st.selectbox("Select Previous Week Sheet", sheet_names, key="prev")

        if current_sheet and previous_sheet:
            st.session_state.current_sheet = current_sheet
            st.session_state.previous_sheet = previous_sheet
            st.session_state.current_week_df = xl.parse(current_sheet)
            st.session_state.previous_week_df = xl.parse(previous_sheet)

elif page == "📊 Quarter Summary Dashboard":
    st.title("📈 Quarter Summary Dashboard")

    if st.session_state.uploaded_file is None:
        st.warning("⚠️ Please upload an Excel file and select sheets from the Data Input page.")
    else:
        current_df = st.session_state.current_week_df
        previous_df = st.session_state.previous_week_df

        col1, col2 = st.columns(2)
        with col1:
            quarter_filter = st.selectbox("Select Quarter", current_df["Quarter"].dropna().unique())
        with col2:
            sales_owner_filter = st.selectbox("Select Sales Owner", current_df["Sales Owner"].dropna().unique())

        # Filter data
        curr_filtered = current_df[(current_df["Quarter"] == quarter_filter) & (current_df["Sales Owner"] == sales_owner_filter)]
        prev_filtered = previous_df[(previous_df["Quarter"] == quarter_filter) & (previous_df["Sales Owner"] == sales_owner_filter)]

        def summarize(df, status):
            return df[df['Status'] == status].groupby('Sales Owner')['Amount'].sum().reset_index()

        # Committed
        committed_current = summarize(curr_filtered, 'Committed for the Month')
        committed_previous = summarize(prev_filtered, 'Committed for the Month')
        committed = pd.merge(committed_current, committed_previous, on='Sales Owner', how='outer', suffixes=(' (Current Week)', ' (Previous Week)')).fillna(0)
        committed['Δ Committed'] = committed['Amount (Current Week)'] - committed['Amount (Previous Week)']
        committed = committed.rename(columns={'Amount (Current Week)': 'Committed (Current Week)', 'Amount (Previous Week)': 'Committed (Previous Week)'})
        committed[['Committed (Current Week)', 'Committed (Previous Week)', 'Δ Committed']] = committed[['Committed (Current Week)', 'Committed (Previous Week)', 'Δ Committed']] / 1e5
        committed[['Committed (Current Week)', 'Committed (Previous Week)', 'Δ Committed']] = committed[['Committed (Current Week)', 'Committed (Previous Week)', 'Δ Committed']].round(0).astype(int)

        # Upside
        upside_current = summarize(curr_filtered, 'Upside for the Month')
        upside_previous = summarize(prev_filtered, 'Upside for the Month')
        upside = pd.merge(upside_current, upside_previous, on='Sales Owner', how='outer', suffixes=(' (Current Week)', ' (Previous Week)')).fillna(0)
        upside['Δ Upside'] = upside['Amount (Current Week)'] - upside['Amount (Previous Week)']
        upside = upside.rename(columns={'Amount (Current Week)': 'Upside (Current Week)', 'Amount (Previous Week)': 'Upside (Previous Week)'})
        upside[['Upside (Current Week)', 'Upside (Previous Week)', 'Δ Upside']] = upside[['Upside (Current Week)', 'Upside (Previous Week)', 'Δ Upside']] / 1e5
        upside[['Upside (Current Week)', 'Upside (Previous Week)', 'Δ Upside']] = upside[['Upside (Current Week)', 'Upside (Previous Week)', 'Δ Upside']].round(0).astype(int)

        # S.No and Total
        def format_table(df, title):
            df.insert(0, "S. No.", range(1, len(df) + 1))
            total_row = pd.DataFrame([["", "🧮 Total"] + df.iloc[:, 2:].sum(numeric_only=True).tolist()], columns=df.columns)
            df = pd.concat([df, total_row], ignore_index=True)
            st.markdown(f"### {title}")
            st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            format_table(committed, "📑 Commitment Comparison (in ₹ Lakhs)")
        with col2:
            format_table(upside, "🔁 Upside Comparison (in ₹ Lakhs)")
