# TO RUN WITHOUT OUTPUT: & C:\Users\AJohnson\AppData\Local\Microsoft\WindowsApps\python3.13.exe -m pytest
# TO RUN WITH OUTPUT: & C:\Users\AJohnson\AppData\Local\Microsoft\WindowsApps\python3.13.exe -m pytest -s -v

import pandas as pd
from excel_cleaner_layered import clean_value, compare_dataframes

def print_header(title):
    print("\n")
    print("="*len(title))
    print(title)
    print("="*len(title))


# ============================================================
# Test cases for clean_value function
# ============================================================
class TestCleanValue:

    def test_clean_value_removes_spaces_and_lowercases(self):
        value = "  ABC Shop  "
        assert clean_value(value) == "abc shop"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_removes_and_symbol(self):
        value = "Smith &   Co"
        assert clean_value(value) == "smith co"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_apostrophe(self):
        value = "O'Connor's"
        assert clean_value(value) == "o connor s"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_hashtag(self):
        value = "Best #1 Store"
        assert clean_value(value) == "best 1 store"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_slash(self):
        value = "Main St./2nd Ave."
        assert clean_value(value) == "main street 2nd avenue"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_hyphen(self):
        value = "Smith's-Store"
        assert clean_value(value) == "smith s store"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))
        
    def test_clean_value_mixed(self):
        value = "O'Connor's & Smith's Store/Tuck Shop #1"
        assert clean_value(value) == "o connor s smith s store tuck shop 1" 
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_address(self):
        value = "#78cef, Hagley Park Road, Kingston #10"
        assert clean_value(value) == "78cef hagley park road kingston 10"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

    def test_clean_value_street_vs_saint(self):
        value = "8 Cassava st, St. Andrew"
        assert clean_value(value) == "8 cassava street saint andrew"
        print("\nInput: " + value)
        print("Output: " + clean_value(value))

# ============================================================
# Test cases for compare_dataframes function
# ============================================================
class TestCompareDataFrames:

    def show_results(self, matched, not_found):
        print("\n")
        print("\nMatched Records:")
        if matched.empty:
            print("No matches found.")
        else:
            print(matched)

        print("\nNot Found Records:")
        if not_found.empty:
            print("All records matched.")
        else:
            print(not_found)

    def test_exact_match_one_layer(self):
        premises_name = "ABC Shop"
        business_name = "ABC SHOP"
        
        # Make DataFrames with the test values
        df1 = pd.DataFrame({
            "Premises Name": [premises_name]
        })

        df2 = pd.DataFrame({
            "Business Name": [business_name]
        })

        # Compare the DataFrames
        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name"],
            ["Business Name"]
        )

        # Test how many records matched and how many were not found
        assert len(matched) == 1
        assert len(not_found) == 0

        self.show_results(matched, not_found)

    def test_no_match_one_layer(self):
        premises_name = "ABC Shop"
        business_name = "XYZ Store"
        
        # Make DataFrames with the test values
        df1 = pd.DataFrame({
            "Premises Name": [premises_name]
        })

        df2 = pd.DataFrame({
            "Business Name": [business_name]
        })

        # Compare the DataFrames
        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name"],
            ["Business Name"]
        )

        # Test how many records matched and how many were not found
        assert len(matched) == 0
        assert len(not_found) == 1

        self.show_results(matched, not_found)

    def test_same_name_different_address_not_found(self):
        premises_name = "ABC Shop"
        address = "Kingston"
        business_name = "ABC Shop"
        location = "Montego Bay"

        df1 = pd.DataFrame({
            "Premises Name": [premises_name],
            "Address": [address]
        })

        df2 = pd.DataFrame({
            "Business Name": [business_name],
            "Location": [location]
        })

        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name", "Address"],
            ["Business Name", "Location"]
        )

        assert len(matched) == 0
        assert len(not_found) == 1

        self.show_results(matched, not_found)

    def test_duplicate_name_correct_address_matched(self):
        premises_name = "ABC Shop"
        address = "Kingston"
        business_name = "ABC Shop"
        location = "Kingston"

        df1 = pd.DataFrame({
            "Premises Name": [premises_name],
            "Address": [address]
        })

        df2 = pd.DataFrame({
            "Business Name": [business_name],
            "Location": [location]
        })

        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name", "Address"],
            ["Business Name", "Location"]
        )

        assert len(matched) == 1
        assert len(not_found) == 0

        self.show_results(matched, not_found)

    def test_duplicate_name_no_correct_address_not_found(self):

        df1 = pd.DataFrame({
            "Premises Name": ["ABC Shop"],
            "Address": ["Ocho Rios"]
        })

        df2 = pd.DataFrame({
            "Business Name": ["ABC Shop", "ABC Shop"],
            "Location": ["Montego Bay", "Kingston"]
        })

        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name", "Address"],
            ["Business Name", "Location"]
        )

        assert len(matched) == 0
        assert len(not_found) == 1

        self.show_results(matched, not_found)

    def test_three_layer_match(self):
        df1 = pd.DataFrame({
            "Premises Name": ["ABC Shop"],
            "Address": ["Kingston"],
            "Operator": ["John Brown"]
        })

        df2 = pd.DataFrame({
            "Business Name": ["ABC Shop"],
            "Location": ["Kingston"],
            "License Holder": ["John Brown"]
        })

        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name", "Address", "Operator"],
            ["Business Name", "Location", "License Holder"]
        )

        assert len(matched) == 1
        assert len(not_found) == 0

        self.show_results(matched, not_found)

    def test_three_layer_operator_diff_not_found(self):
        df1 = pd.DataFrame({
            "Premises Name": ["ABC Shop"],
            "Address": ["Kingston"],
            "Operator": ["John Brown"]
        })

        df2 = pd.DataFrame({
            "Business Name": ["ABC Shop"],
            "Location": ["Kingston"],
            "License Holder": ["Jane Smith"]
        })

        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name", "Address", "Operator"],
            ["Business Name", "Location", "License Holder"]
        )

        assert len(matched) == 0
        assert len(not_found) == 1

        self.show_results(matched, not_found)

    def test_cleaning_case_and_spaces_still_matches(self):
        df1 = pd.DataFrame({
            "Premises Name": ["  ABC SHOP  "],
            "Address": [" Kingston "]
        })

        df2 = pd.DataFrame({
            "Business Name": ["abc shop"],
            "Location": ["kingston"]
        })

        matched, not_found, review_log = compare_dataframes(
            df1,
            df2,
            ["Premises Name", "Address"],
            ["Business Name", "Location"]
        )

        assert len(matched) == 1
        assert len(not_found) == 0

        self.show_results(matched, not_found)