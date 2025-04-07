
from pathlib import Path
import pandas as pd
import streamlit as st

# Set page config
st.set_page_config(layout="wide", page_title="Weekly Commitment Comparison Tool")

# Initialize state
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "sheet_names" not in st.session_state:
    st.session_state.sheet_names = []

# Navigation
page = st.sidebar.radio("Navigate", ["📂 Data Input", "📊 Quarter Summary Dashboard"])

# Page 1
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

# Page 2
elif page == "📊 Quarter Summary Dashboard":
    st.title("📊 Quarter Summary Dashboard")

    if not st.session_state.uploaded_file:
        st.warning("⚠️ Please upload a file in the 'Data Input' page.")
        st.stop()

    # Load Excel data
    xls = pd.ExcelFile(st.session_state.uploaded_file)
    df_current = pd.read_excel(xls, sheet_name=st.session_state.get("current_sheet", "Raw_Data"))
    df_previous = pd.read_excel(xls, sheet_name=st.session_state.get("previous_sheet", "PreviousWeek_Raw_Data"))

    # Clean and prepare
    def preprocess(df):
        df["Quarter"] = df["Quarter"].astype(str).str.strip()
        df["Sales Owner"] = df["Sales Owner"].astype(str).str.strip()
        df["Status"] = df["Status"].astype(str).str.strip()
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        return df

    df_current = preprocess(df_current)
    df_previous = preprocess(df_previous)

    # Filter dropdowns
    quarters = sorted(set(df_current["Quarter"].unique()) | set(df_previous["Quarter"].unique()))
    selected_quarter = st.selectbox("Select Quarter", quarters)
    sales_owners = sorted(set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique()))
    selected_owner = st.selectbox("Select Sales Owner", ["All"] + sales_owners)

    # Filter logic
    def filter_data(df, status):
        df = df[df["Quarter"] == selected_quarter]
        if selected_owner != "All":
            df = df[df["Sales Owner"] == selected_owner]
        return df[df["Status"] == status]

    df_commit_current = filter_data(df_current, "Committed for the Month")
    df_commit_previous = filter_data(df_previous, "Committed for the Month")
    df_upside_current = filter_data(df_current, "Upside for the Month")
    df_upside_previous = filter_data(df_previous, "Upside for the Month")

    # Prepare summary tables
    all_owners = pd.DataFrame({"Sales Owner": sales_owners})

    def agg_amount(df):
        return df.groupby("Sales Owner")["Amount"].sum().reset_index()

    def prepare_table(cur, prev, value_name):
        cur = agg_amount(cur).rename(columns={"Amount": f"{value_name} (Current Week)"})
        prev = agg_amount(prev).rename(columns={"Amount": f"{value_name} (Previous Week)"})
        df = all_owners.merge(cur, on="Sales Owner", how="left").merge(prev, on="Sales Owner", how="left").fillna(0)
        df[f"Δ {value_name}"] = df[f"{value_name} (Current Week)"] - df[f"{value_name} (Previous Week)"]
        df = df.round(0)
        return df

    commit_table = prepare_table(df_commit_current, df_commit_previous, "Committed")
    upside_table = prepare_table(df_upside_current, df_upside_previous, "Upside")

    # Convert to ₹ Lakhs
    for col in commit_table.columns[1:]:
        commit_table[col] = (commit_table[col] / 1e5).astype(int)
    for col in upside_table.columns[1:]:
        upside_table[col] = (upside_table[col] / 1e5).astype(int)

    # Add total row
    def add_total_row(df, label="📊 Total"):
        total = pd.DataFrame([[
            label] + [df[col].sum() for col in df.columns[1:]]
        ], columns=df.columns)
        return pd.concat([df, total], ignore_index=True)

    commit_table = add_total_row(commit_table)
    upside_table = add_total_row(upside_table)

    # Add S. No. column
    def add_sno(df):
        df.insert(0, "S. No.", range(1, len(df)+1))
        df.loc[df["Sales Owner"].str.contains("Total"), "S. No."] = ""
        return df

    commit_table = add_sno(commit_table)
    upside_table = add_sno(upside_table)

    # Display side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🧾 Commitment Comparison (in ₹ Lakhs)")
        st.dataframe(commit_table, use_container_width=True)
    with col2:
        st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
        st.dataframe(upside_table, use_container_width=True)
