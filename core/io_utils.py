import os
import pandas as pd


def file_exists(file_path):
    return os.path.exists(file_path)


def load_excel_file(file_path):
    return pd.read_excel(file_path, engine="openpyxl")



def write_results_to_excel(
    matched_df,
    not_found_df,
    review_log_df,
    output_file
):
    # Delete old output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Write only three sheets: Matched, Not Found, and Review Log
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        
        # "Matched" Sheet
        matched_df.to_excel(
            writer,
            sheet_name="Matched",
            index=False
        )

        # "Not Found" Sheet
        not_found_df.to_excel(
            writer,
            sheet_name="Not Found",
            index=False
        )

        # "Review Log" Sheet    
        review_log_df.to_excel(
            writer,
            sheet_name="Review Log",
            index=False
        )
