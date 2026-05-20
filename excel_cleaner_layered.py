import pandas as pd
import os

# Threshold for fuzzy matching (0-100). Adjust as needed.
FUZZY_THRESHOLD = 50





def main():
    print("=== Excel File Comparison Tool ===\n")

    downloads_folder = os.path.join(
    os.path.expanduser("~"),
    "Downloads"
    )

    output_file = os.path.join(
        downloads_folder,
        "Comparison_Result.xlsx"
    )

    file1 = input("Enter first Excel file name/path: ").strip()
    file2 = input("Enter second Excel file name/path: ").strip()

    if not file_exists(file1):
        print(f"\nError: '{file1}' was not found.")
        exit()

    if not file_exists(file2):
        print(f"\nError: '{file2}' was not found.")
        exit()

    try:
        # Load Excel files
        df1 = load_excel_file(file1)
        df2 = load_excel_file(file2)

        # Confirm files loaded successfully
        print("\nFiles loaded successfully.")

        # Show columns in both files
        print(f"\nColumns in {file1}:")
        for col in df1.columns:
            print(f"- {col}")

        print(f"\nColumns in {file2}:")
        for col in df2.columns:
            print(f"- {col}")

        # Ask how many comparison layers the user wants
        num_layers = int(
            input("\nHow many column pairs do you want to compare? ")
        )

        file1_columns = []
        file2_columns = []

        # Get comparison columns from user
        for i in range(num_layers):
            print(f"\nComparison Layer {i + 1}")

            col1 = input(f"Enter column from {file1}: ").strip()
            col2 = input(f"Enter matching column from {file2}: ").strip()

            if col1 not in df1.columns:
                print(f"\nError: Column '{col1}' not found in {file1}.")
                exit()

            if col2 not in df2.columns:
                print(f"\nError: Column '{col2}' not found in {file2}.")
                exit()

            file1_columns.append(col1)
            file2_columns.append(col2)

        matched_df, not_found_df, review_log_df = compare_dataframes(
            df1,
            df2,
            file1_columns,
            file2_columns
        )

        write_results_to_excel(
            matched_df,
            not_found_df,
            review_log_df,
            output_file
        )

        print("\nComparison complete.")
        print(f"Results saved to '{output_file}'")
        print(f"\nMatched Records: {len(matched_df)}")
        print(f"Not Found Records: {len(not_found_df)}")

    except PermissionError as e:
        print("\nPermission error.")
        print("Close any Excel files being used by this script.")
        print(f"\nTechnical detail: {e}")

    except ValueError:
        print("\nError: Please enter a valid number for comparison layers.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()