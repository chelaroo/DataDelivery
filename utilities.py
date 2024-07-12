import pandas as pd
from fuzzywuzzy import fuzz

def convert_categorical_to_lowercase(df):
    """
    Convert all categorical (object type) columns in the DataFrame to lowercase.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with all object type columns converted to lowercase.
    """    
    categorical_columns = df.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        df[col] = df[col].str.lower()
    return df

def filter_non_null(df, columns):
    """
    Remove rows that have all null values in the specified columns.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of columns to check for non-null values.

    Returns:
        pd.DataFrame: The DataFrame with rows removed if all specified columns are null.
    """    
    return df.dropna(subset=columns, how='all')

def similarity_score(str1, str2):
    """
    Calculate the similarity score between two strings using fuzzy matching.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        int: The similarity score between 0 and 100.
    """    
    if pd.isna(str1) or pd.isna(str2):
        return 0
    return fuzz.token_sort_ratio(str1, str2)

# Function to check if a string contains more detail than another
def is_more_detailed(base, new):
    """
    Check if the new string contains more details than the base string.

    Args:
        base (str): The base string.
        new (str): The new string.

    Returns:
        bool: True if the new string is more detailed, otherwise False.
    """    
    if pd.isna(base) or pd.isna(new):
        return False
    base_tokens = set(base.split())
    new_tokens = set(new.split())
    return new_tokens.issuperset(base_tokens)

# Function to resolve conflicts and handle similar data
def resolve_conflict(row, columns):
    """
    Resolve conflicts and handle similar data across multiple columns.

    Args:
        row (pd.Series): The row of the DataFrame.
        columns (list): The list of columns to resolve conflicts for.

    Returns:
        pd.Series: The row with resolved conflicts.
    """    
    result = {}
    for col in columns:
        website_col = f"{col}_website"
        facebook_col = f"{col}_facebook"
        google_col_unique = f"{col}_google_unique"
        google_col_non_unique_reliable = f"{col}_google_non_unique_reliable"
        google_col_non_unique_less_reliable = f"{col}_google_non_unique_less_reliable"
        
        values = {
            'website': row[website_col] if website_col in row and pd.notna(row[website_col]) else None,
            'google_unique': row[google_col_unique] if google_col_unique in row and pd.notna(row[google_col_unique]) else None,
            'google_non_unique_reliable': row[google_col_non_unique_reliable] if google_col_non_unique_reliable in row and pd.notna(row[google_col_non_unique_reliable]) else None,
            'facebook': row[facebook_col] if facebook_col in row and pd.notna(row[facebook_col]) else None,
            'google_non_unique_less_reliable': row[google_col_non_unique_less_reliable] if google_col_non_unique_less_reliable in row and pd.notna(row[google_col_non_unique_less_reliable]) else None
        }
        
        non_null_values = {k: v for k, v in values.items() if v}
        
        if not non_null_values:
            result[col] = None
            continue
        
        best_value = next(iter(non_null_values.values()), None)
        best_score = 100 if best_value else 0
        
        for _ , value in non_null_values.items():
            if value and value != best_value:
                score = similarity_score(best_value, value)
                if score > best_score:
                    best_value = value
                    best_score = score
                elif score >= 75 and is_more_detailed(best_value, value):  # Append if more detailed
                    best_value = f"{best_value}, {value}"
        
        result[col] = best_value
    return pd.Series(result)

def resolve_name_phone(row):
    """
    Resolve conflicts for 'name' and 'phone' columns with prioritization.

    Args:
        row (pd.Series): The row of the DataFrame.

    Returns:
        pd.Series: The row with resolved 'name' and 'phone'.
    """    
    sources = ['website', 'google_unique', 'google_non_unique_reliable', 'facebook', 'google_non_unique_less_reliable']
    for source in sources:
        if pd.notna(row[f'name_{source}']):
            row['name'] = row[f'name_{source}']
            break
    for source in sources:
        if pd.notna(row[f'phone_{source}']):
            row['phone'] = row[f'phone_{source}']
            break
    return row