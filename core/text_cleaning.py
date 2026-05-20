import re
import unicodedata
from rapidfuzz import fuzz


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