import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Commitment Comparison", layout="wide")

st.title("📊 Weekly Commitment Comparison Tool")

uploaded_file = st.file_uploader("📁 Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        st.success("✅ Excel file loaded successfully!")

        current_sheet = st.selectbox("Select Current Week Sheet", sheet_names, key="current")
        previous_sheet = st.selectbox("Select Previous Week Sheet", sheet_names, key="previous")

        current_week_df = pd.read_excel(xls, sheet_name=current_sheet)
        previous_week_df = pd.read_excel(xls, sheet_name=previous_sheet)

        # Show filters
        quarters = sorted(current_week_df['Quarter'].dropna().unique())
        sales_owners = sorted(current_week_df['Sales Owner'].dropna().unique())

        selected_quarter = st.selectbox("📅 Select Quarter", quarters)
        selected_sales_owner = st.selectbox("🧑‍💼 Select Sales Owner", ["All"] + sales_owners)

        # Apply filters
        current_week_df = current_week_df[current_week_df["Quarter"] == selected_quarter]
        previous_week_df = previous_week_df[previous_week_df["Quarter"] == selected_quarter]

        if selected_sales_owner != "All":
            current_week_df = current_week_df[current_week_df["Sales Owner"] == selected_sales_owner]
            previous_week_df = previous_week_df[previous_week_df["Sales Owner"] == selected_sales_owner]

        def generate_summary(status_filter, label):
            current_filtered = current_week_df[current_week_df["Status"] == status_filter]
            previous_filtered = previous_week_df[previous_week_df["Status"] == status_filter]

            current_sum = current_filtered.groupby("Sales Owner")["Amount"].sum().div(1e5).round()
            previous_sum = previous_filtered.groupby("Sales Owner")["Amount"].sum().div(1e5).round()

            df_summary = pd.DataFrame({
                f"{label} (Current Week)": current_sum,
                f"{label} (Previous Week)": previous_sum
            }).fillna(0)

            df_summary[f"Δ {label}"] = df_summary[f"{label} (Current Week)"] - df_summary[f"{label} (Previous Week)"]
            df_summary = df_summary.reset_index()

            # Convert to integers
            for col in df_summary.columns[1:]:
                df_summary[col] = df_summary[col].astype(int)

            # Sort Sales Owners
            df_summary = df_summary.sort_values(by="Sales Owner").reset_index(drop=True)

            # Add Serial Number
            df_summary.insert(0, "S. No.", range(1, len(df_summary) + 1))

            # Add Total row
            totals = {
                "S. No.": "",
                "Sales Owner": "🔢 Total",
                f"{label} (Current Week)": df_summary[f"{label} (Current Week)"].sum(),
                f"{label} (Previous Week)": df_summary[f"{label} (Previous Week)"].sum(),
                f"Δ {label}": df_summary[f"Δ {label}"].sum(),
            }
            df_summary = pd.concat([df_summary, pd.DataFrame([totals])], ignore_index=True)

            return df_summary

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧾 Commitment Comparison (in ₹ Lakhs)")
            committed_df = generate_summary("Committed for the Month", "Committed")
            st.dataframe(committed_df, use_container_width=True)

        with col2:
            st.subheader("🔁 Upside Comparison (in ₹ Lakhs)")
            upside_df = generate_summary("Upside for the Month", "Upside")
            st.dataframe(upside_df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")
else:
    st.info("📤 Please upload an Excel file to get started.")
