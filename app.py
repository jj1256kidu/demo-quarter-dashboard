import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(layout="wide", page_title="Weekly Commitment Comparison Tool")

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'sheet_names' not in st.session_state:
    st.session_state.sheet_names = []

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["📂 Data Input", "📊 Quarter Summary Dashboard"])

# Page 1: Data Input
if page == "📂 Data Input":
    st.title("📈 Weekly Commitment Comparison Tool")
    st.markdown("#### 📁 Upload Excel file")

    uploaded_file = st.file_uploader("Drag and drop file here", type=["xlsx"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        xls = pd.ExcelFile(uploaded_file)
        st.session_state.sheet_names = xls.sheet_names
        st.success("✅ Excel file loaded successfully!")

    if st.session_state.sheet_names:
        sheet1 = st.selectbox("Select Current Week Sheet", st.session_state.sheet_names, key="current_sheet")
        sheet2 = st.selectbox("Select Previous Week Sheet", st.session_state.sheet_names, key="previous_sheet")

# Page 2: Quarter Summary Dashboard
elif page == "📊 Quarter Summary Dashboard":
    st.title("📊 Quarter Summary Dashboard")

    if not st.session_state.uploaded_file:
        st.warning("⚠️ Please upload a file in the 'Data Input' page.")
        st.stop()

    # Load selected sheets
    xls = pd.ExcelFile(st.session_state.uploaded_file)
    df_current = pd.read_excel(xls, sheet_name=st.session_state.get("current_sheet", "Raw_Data"))
    df_previous = pd.read_excel(xls, sheet_name=st.session_state.get("previous_sheet", "PreviousWeek_Raw_Data"))

    # Clean and prepare data
    def preprocess(df):
        df["Quarter"] = df["Quarter"].astype(str).str.strip()
        df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
        df["Status"] = df["Status"].astype(str).str.strip()
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        return df

    df_current = preprocess(df_current)
    df_previous = preprocess(df_previous)

    # Filter options
    quarters = sorted((set(df_current["Quarter"].unique()) | set(df_previous["Quarter"].unique())) - {"nan", "None", ""})
    selected_quarter = st.selectbox("Select Quarter", quarters)

    sales_owners = sorted((set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique())) - {"nan", "None", ""})
    selected_owner = st.selectbox("Select Sales Owner", ["All"] + sales_owners)

    # Filter based on quarter and (optional) sales owner
    def filter_data(df, status_type):
        if selected_quarter != "All":
            df = df[df["Quarter"] == selected_quarter]
        if selected_owner != "All":
            df = df[df["Sales Owner"] == selected_owner]
        return df[df["Status"] == status_type]

    df_commit_current = filter_data(df_current, "Committed for the Month")
    df_commit_previous = filter_data(df_previous, "Committed for the Month")
    df_upside_current = filter_data(df_current, "Upside for the Month")
    df_upside_previous = filter_data(df_previous, "Upside for the Month")
    df_closed_current = filter_data(df_current, "Closed Won")
    df_closed_previous = filter_data(df_previous, "Closed Won")

    # Aggregation
    def agg_amount(df):
        return df.groupby("Sales Owner")["Amount"].sum().reset_index()

    unique_owners = sorted((set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique())) - {"nan", "None", ""})
    all_owners_df = pd.DataFrame({"Sales Owner": unique_owners})

    def prepare_table(cur, prev, value_name):
        cur = agg_amount(cur).rename(columns={"Amount": f"Amount (Current Week)"})
        prev = agg_amount(prev).rename(columns={"Amount": f"Amount (Previous Week)"})
        df = all_owners_df.merge(cur, on="Sales Owner", how="left").merge(prev, on="Sales Owner", how="left").fillna(0)
        df[f"∆ {value_name}"] = df[f"Amount (Current Week)"] - df[f"Amount (Previous Week)"]
        df = df.round(0)
        return df

    def add_total_row(df, label="\U0001F4C8 Total"):
        total = df.drop(columns=["S. No."], errors="ignore").sum(numeric_only=True)
        total_row = pd.DataFrame([[label] + total.tolist()], columns=["Sales Owner"] + list(total.index))
        df = pd.concat([df, total_row], ignore_index=True)
        return df

    def add_serial_numbers(df):
        df.insert(0, "S. No.", range(1, len(df)+1))
        df.loc[df["Sales Owner"] == "\U0001F4C8 Total", "S. No."] = ""
        return df

    commit_table = prepare_table(df_commit_current, df_commit_previous, "Committed")
    upside_table = prepare_table(df_upside_current, df_upside_previous, "Upside")
    closed_table = prepare_table(df_closed_current, df_closed_previous, "Closed Won")

    for table in [commit_table, upside_table, closed_table]:
        for col in table.columns[1:]:
            table[col] = (table[col] / 1e5).astype(int)
        table = add_total_row(table)
        table = add_serial_numbers(table)

    commit_table = add_total_row(commit_table)
    commit_table = add_serial_numbers(commit_table)
    upside_table = add_total_row(upside_table)
    upside_table = add_serial_numbers(upside_table)
    closed_table = add_total_row(closed_table)
    closed_table = add_serial_numbers(closed_table)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 📝 Commitment Comparison (in ₹ Lakhs)")
        st.dataframe(commit_table, use_container_width=True)

    with col2:
        st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
        st.dataframe(upside_table, use_container_width=True)

    with col3:
        st.markdown("### ✅ Closed Won Comparison (in ₹ Lakhs)")
        st.dataframe(closed_table, use_container_width=True)

    with col4:
        st.markdown("### 📊 Overall Committed + Closed Won (in ₹ Lakhs)")
        overall_table = commit_table.copy()
        overall_table["Overall Committed + Closed Won (Current Week)"] = overall_table["Amount (Current Week)"] + closed_table["Amount (Current Week)"]
        overall_table["Overall Committed + Closed Won (Previous Week)"] = overall_table["Amount (Previous Week)"] + closed_table["Amount (Previous Week)"]
        overall_table["∆ Overall Committed + Closed Won"] = overall_table["Overall Committed + Closed Won (Current Week)"] - overall_table["Overall Committed + Closed Won (Previous Week)"]
        st.dataframe(overall_table, use_container_width=True)
