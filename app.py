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
