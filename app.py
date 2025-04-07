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

        # Create a DataFrame with all sales owners to ensure all appear in the final tables
        all_sales_owners = sorted(set(df_current["Sales Owner"].unique()) | set(df_previous["Sales Owner"].unique()) - {"nan", "None", ""})
        all_owners_df = pd.DataFrame({"Sales Owner": all_sales_owners})

        def prepare_table(cur, prev, value_name):
            cur = agg_amount(cur).rename(columns={"Amount": f"Amount (Current Week)"})
            prev = agg_amount(prev).rename(columns={"Amount": f"Amount (Previous Week)"})
            df = pd.merge(all_owners_df, cur, on="Sales Owner", how="left").merge(prev, on="Sales Owner", how="left").fillna(0)
            df[f"∆ {value_name}"] = df[f"Amount (Current Week)"] - df[f"Amount (Previous Week)"]
            df = df[["Sales Owner", f"Amount (Current Week)", f"Amount (Previous Week)", f"∆ {value_name}"]]  # Remove S. No.
            df = df.round(0)
            return df

        # Prepare tables for Commitment, Upside, Closed Won
        commit_table = prepare_table(df_commit_current, df_commit_previous, "Committed")
        upside_table = prepare_table(df_upside_current, df_upside_previous, "Upside")
        closed_table = prepare_table(df_closed_current, df_closed_previous, "Closed Won")

        # Concatenate Commit and Closed Won for overall table
        overall_table = pd.concat([df_commit_current, df_closed_current], ignore_index=True)
        overall_table_previous = pd.concat([df_commit_previous, df_closed_previous], ignore_index=True)
        overall_table = prepare_table(overall_table, overall_table_previous, "Committed + Closed Won")

        # Remove rows where Sales Owner is 'nan'
        def remove_nan_sales_owner(df):
            return df[df["Sales Owner"].str.lower() != "nan"]

        # Apply the removal function
        commit_table = remove_nan_sales_owner(commit_table)
        upside_table = remove_nan_sales_owner(upside_table)
        closed_table = remove_nan_sales_owner(closed_table)
        overall_table = remove_nan_sales_owner(overall_table)

        # Remove Sales Owner column from view (keep it in data)
        commit_table = commit_table.drop(columns=["Sales Owner"])
        upside_table = upside_table.drop(columns=["Sales Owner"])
        closed_table = closed_table.drop(columns=["Sales Owner"])
        overall_table = overall_table.drop(columns=["Sales Owner"])

        # Create columns for layout
        col1, col2, col3, col4 = st.columns(4)

        # Display Commitment Table
        with col1:
            st.markdown("### 📝 Commitment Comparison (in ₹ Lakhs)")
            st.dataframe(commit_table, use_container_width=True)

        # Display Upside Table
        with col2:
            st.markdown("### 🔁 Upside Comparison (in ₹ Lakhs)")
            st.dataframe(upside_table, use_container_width=True)

        # Display Closed Won Table
        with col3:
            st.markdown("### ✅ Closed Won Comparison (in ₹ Lakhs)")
            st.dataframe(closed_table, use_container_width=True)

        # Display Overall Committed + Closed Won Table
        with col4:
            st.markdown("### 📊 Overall Committed + Closed Won (in ₹ Lakhs)")
            st.dataframe(overall_table, use_container_width=True)

except ModuleNotFoundError as e:
    print("Required module not found:", e)
    print("Please ensure Streamlit is installed in your environment.")
