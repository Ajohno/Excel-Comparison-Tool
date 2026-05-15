import pandas as pd
import os
import re
import unicodedata
from rapidfuzz import fuzz

# Threshold for fuzzy matching (0-100). Adjust as needed.
FUZZY_THRESHOLD = 50

# Dictionary of common address abbreviations and their expansions
ADDRESS_ABBREVIATIONS = {
    "rd": "road",
    "rd.": "road",
    "ave": "avenue",
    "ave.": "avenue",
    "blvd": "boulevard",
    "blvd.": "boulevard",
    "dr": "drive",
    "dr.": "drive",
    "ln": "lane",
    "ln.": "lane",
    "hwy": "highway",
    "hwy.": "highway",
}

# Calculates a fuzzy similarity score between two values
def fuzzy_score(value1, value2):
    return fuzz.token_sort_ratio(
        clean_value(value1),
        clean_value(value2)
    )

# Cleans values before comparing
def clean_value(value):
    value = str(value)

    # Normalize Unicode characters
    value = unicodedata.normalize("NFKD", value)

    # Remove accents
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )

    # Lowercase
    value = value.lower()

    #Differentiate between "st" as street and "st" as saint

    # Dictionary of the parishes in Jamaica with "St."
    saint_places = [
        "andrew",
        "ann",
        "catherine",
        "james",
        "mary",
        "thomas",
        "elizabeth"
    ] 

    # Replace "st" with "street" only when it is followed by a known place name that indicates it's likely a saint reference
    for place in saint_places:
        value = re.sub(
            rf"\bst\.?\s+{place}\b",
            f"saint {place}",
            value
        )


    # Replace punctuation with space to prevent word from merging
    # This will remove characters like &, #, ', /, etc.
    value = re.sub(r"[^\w\s]", " ", value)

    # Normalize address abbreviations
    words = value.split()

    normalized_words = []

    for word in words:
        if word in ADDRESS_ABBREVIATIONS:
            normalized_words.append(ADDRESS_ABBREVIATIONS[word])
        elif word == "st":
            normalized_words.append("street")
        else:
            normalized_words.append(word)

    # Join the normalized words back into a single string
    value = " ".join(normalized_words)

    # Collapse extra spaces
    value = re.sub(r"\s+", " ", value).strip()

    return value


def file_exists(file_path):
    return os.path.exists(file_path)


def load_excel_file(file_path):
    return pd.read_excel(file_path, engine="openpyxl")


def create_clean_columns(df1, df2, file1_columns, file2_columns):
    num_layers = len(file1_columns)

    for i in range(num_layers):
        df1[f"_clean_{i}"] = df1[file1_columns[i]].apply(clean_value)
        df2[f"_clean_{i}"] = df2[file2_columns[i]].apply(clean_value)

    return df1, df2


def compare_dataframes(df1, df2, file1_columns, file2_columns):
    num_layers = len(file1_columns)

    df1, df2 = create_clean_columns(
        df1,
        df2,
        file1_columns,
        file2_columns
    )

    # Different sheets in the Excel output file
    matched_records = []
    not_found_records = []
    review_log = []

    # Compare each row from File 1 against File 2
    for _, row1 in df1.iterrows():

        # Keep track of how many records match at each layer for review purposes
        layer_match_counts = []

        # Start by comparing the first selected column
        possible_matches = df2[
            df2["_clean_0"] == row1["_clean_0"]
        ]
        # Record how many matches we got on the first layer before applying further layers
        layer_match_counts.append(len(possible_matches))

        # If there is no match on the first column, record is not found
        if possible_matches.empty:
            not_found_records.append(row1)
            continue

        # Compare the remaining selected columns one layer at a time
        for i in range(1, num_layers):

            possible_matches = possible_matches[
                possible_matches[f"_clean_{i}"] == row1[f"_clean_{i}"]
            ]

            # Record how many matches we got at this layer before applying further layers
            layer_match_counts.append(len(possible_matches))

            # Stop immediately if a layer fails
            if possible_matches.empty:
                break

        if not possible_matches.empty:
            matched_records.append(row1)
            final_result = "Matched"
            fuzzy_best_score = ""
        else:
            fuzzy_best_score = 0

            # Try fuzzy matching against File 2 records that matched Layer 1/name
            name_matches = df2[
                df2["_clean_0"] == row1["_clean_0"]
            ]

            if not name_matches.empty and num_layers > 1:
                for _, row2 in name_matches.iterrows():
                    score = fuzzy_score(
                        row1[file1_columns[1]],
                        row2[file2_columns[1]]
                    )

                    if score > fuzzy_best_score:
                        fuzzy_best_score = score

                if fuzzy_best_score >= FUZZY_THRESHOLD:
                    matched_records.append(row1)
                    final_result = "Probable Match"
                else:
                    not_found_records.append(row1)
                    final_result = "Not Found"
            else:
                not_found_records.append(row1)
                final_result = "Not Found"

        # Create a review log entry for this record
        log_entry = {
            "Result": final_result,
            "Layer Match Counts": str(layer_match_counts),
            "Best Comparison Score": fuzzy_best_score
        }
        # Add original and cleaned values for each layer
        for i in range(num_layers):

            # Add original value for this layer's column
            log_entry[f"Original Layer {i+1}"] = row1[file1_columns[i]]
            # Add cleaned value for this layer's column
            log_entry[f"Cleaned Layer {i+1}"] = row1[f"_clean_{i}"]

        # Add the log entry to the review log
        review_log.append(log_entry)

    matched_df = pd.DataFrame(matched_records)
    not_found_df = pd.DataFrame(not_found_records)
    review_log_df = pd.DataFrame(review_log)

    # Remove helper columns from output
    helper_columns = [f"_clean_{i}" for i in range(num_layers)]

    matched_df = matched_df.drop(
        columns=helper_columns,
        errors="ignore"
    )

    not_found_df = not_found_df.drop(
        columns=helper_columns,
        errors="ignore"
    )

    return matched_df, not_found_df, review_log_df


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