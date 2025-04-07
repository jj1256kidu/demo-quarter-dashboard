# This version avoids importing `streamlit` in environments without it.
try:
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
    page = st.sidebar.radio("Navigate", ["F4C2 Data Input", "F4CA Quarter Summary Dashboard"])

    # Page 1: Data Input
    if page == "F4C2 Data Input":
        st.title("F4C8 Weekly Commitment Comparison Tool")
        st.markdown("#### F4C1 Upload Excel file")

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
    elif page == "F4CA Quarter Summary Dashboard":
        st.title("F4CA Quarter Summary Dashboard")

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
        quarters.insert(0, "All")
        selected_quarter = st.selectbox("Select Quarter", quarters)

        sales_owners = sorted((set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique())) - {"nan", "None", ""})
        sales_owners.insert(0, "All")
        selected_owner = st.selectbox("Select Sales Owner", sales_owners)

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

        closed_table = prepare_table(df_closed_current, df_closed_previous, "Closed Won")

        for col in closed_table.columns[1:]:
            closed_table[col] = (closed_table[col] / 1e5).astype(int)

        def add_total_row(df, label="\U0001F4C8 Total"):
            total = df.drop(columns=["S. No."], errors="ignore").sum(numeric_only=True)
            total_row = pd.DataFrame([[label] + total.tolist()], columns=["Sales Owner"] + list(total.index))
            df = pd.concat([df, total_row], ignore_index=True)
            return df

        def add_serial_numbers(df):
            df.insert(0, "S. No.", range(1, len(df)+1))
            df.loc[df["Sales Owner"] == "\U0001F4C8 Total", "S. No."] = ""
            return df

        closed_table = add_total_row(closed_table)
        closed_table = add_serial_numbers(closed_table)

        st.markdown("### \U00002705 Closed Won Comparison (in ₹ Lakhs)")
        st.dataframe(closed_table, use_container_width=True)

except ModuleNotFoundError as e:
    print("Required module not found:", e)
    print("Please ensure Streamlit is installed in your environment.")
