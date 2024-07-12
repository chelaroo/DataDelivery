## Overview
\
NOTE: Please create a directory 'datasets' with the three datasets: website, facebook and google 
\
This project aims to merge data from multiple sources, resolve conflicts between similar data entries, and save the final cleaned data into an Excel file. The main sources of data are:
- Website data
- Facebook data
- Google data

## Initial observations

1. Website and Facebook data are unique at domain level
2. Google data is not unique at domain level
3. There are rows that don't have information on none of the columns of interest
4. Google dataset contains data from various sources, including facebook
5. All observations from facebook data are also in website data
6. 55k domains are unique in the google data 
7. The rest of non unique domains should be joined on other fields
8. There is a need to constrain the non_unique domain joins since I don't want an artificial increase on the number of observations

## Project Steps 

1. **Convert Categorical Columns to Lowercase**: 
   - Ensures consistent comparison of string data by converting all text to lowercase

2. **Filter Non-Null Rows**:
   - Removes rows that have null values in all the specified columns of interest to avoid unnecessary data processing

3. **Merge Data**:
   - Left joins website data with Facebook data based on the domain (all facebook data is included in website data)
   - Separates Google data into unique and non-unique domains
   - Outer joins website&facebook data with unique domain google data: this way everything is kept and what is matched will improve quality on columns of interest
   - Left joins the merged data with non unique domain google data on [domain, company name, country and city]: getting rid of join conditions (like joining on company name and country results in bad matches and quality drop)
   - Outer joins unmatched google data with the merged data to get a full picture which is as accurate as possible 
   - Renames columns of interest for better understanding

4. **Resolve Conflicts**:
   - Resolves conflicts in columns 'Category' and 'Address': assigns a score to the first value found in one of the deciding columns. Then it does a similarity check with the other columns to find more complete versions. The score doesn't have to match the initial score assigned of 100. If it's over 75 but is more detailed, it gets updated 
   - Resolves conflicts in columns 'Name' and 'Phone': this is a priority based approach (subjective to one's views): mine was (from most important to least important) - website data -> google unique -> google non unique reliable -> facebook data -> google non unique less reliable

6. **Save Final Data**:
   - Creates output directory if it doesn't exist
   - Saves the cleaned and resolved data into an Excel file in the specified output directory

## How to Run

1. **Ensure Dependencies are Installed**:
   - Install necessary libraries using:
     ```sh
     pip install pandas fuzzywuzzy openpyxl
     ```

2. **Run the Main Script**:
   - Execute the main script:
     ```sh
     python main.py
     ```

3. **Output**:
   - The final cleaned data will be saved in the `out` directory as `company_data.xlsx`.

## Functions Explanation

### utilities.py

- **convert_categorical_to_lowercase(df)**:
  - Converts all categorical (object type) columns in the DataFrame to lowercase to ensure consistency

- **filter_non_null(df, columns)**:
  - Filters out rows that have all null values in the specified columns to focus only on relevant data

- **similarity_score(str1, str2)**:
  - Computes the similarity score between two strings using fuzzy matching to assist in conflict resolution

- **is_more_detailed(base, new)**:
  - Checks if the new string contains more details compared to the base string, aiding in data conflict resolution

- **resolve_conflict(row, columns)**:
  - Resolves conflicts in specified columns by choosing the most reliable and detailed information

- **resolve_name_phone(row)**:
  - Prioritizes 'name' and 'phone' columns based on a predefined order of reliability from different data sources

- **remove_semicolons(column)**:
  - Removes semicolons from column values to ensure clean CSV output

### main.py

- **main()**:
  - Loads datasets, processes the data through various steps including merging and conflict resolution, and saves the final output.

## Notes

- Ensure the datasets (`website_dataset.csv`, `facebook_dataset.csv`, `google_dataset.csv`) are available in the `datasets` directory
- The output directory will be created automatically if it does not exist
- The script is designed to handle missing data gracefully and prioritize more reliable sources
