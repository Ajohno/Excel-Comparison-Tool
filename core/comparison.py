import pandas as pd
import os

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
