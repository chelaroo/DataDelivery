import pandas as pd
import os
from utilities import (
    convert_categorical_to_lowercase,
    filter_non_null,
    resolve_conflict,
    resolve_name_phone
)


def main():
    website_data = pd.read_csv('datasets/website_dataset.csv', sep=';')
    facebook_data = pd.read_csv(
        'datasets/facebook_dataset.csv',  on_bad_lines='skip')
    google_data = pd.read_csv(
        'datasets/google_dataset.csv',  on_bad_lines='skip')

    facebook_data = convert_categorical_to_lowercase(facebook_data)
    google_data = convert_categorical_to_lowercase(google_data)
    website_data = convert_categorical_to_lowercase(website_data)

    # Create address variable in website data by combining country region and city
    website_data['address'] = website_data.apply(
        lambda row: ', '.join(filter(None, [str(row['main_city']).strip(), str(row['main_region']).strip(), str(row['main_country']).strip()])), axis=1)

    # Remove rows that don't have information on none of the columns of interest
    # since it's a pain later on with the joins
    website_data_columns_of_interest = [
        's_category', 'address', 'phone', 'site_name']
    facebook_data_columns_of_interest = [
        'categories', 'address', 'phone', 'name']
    google_data_columns_of_interest = ['category', 'address', 'phone', 'name']

    website_data = filter_non_null(
        website_data, website_data_columns_of_interest)
    facebook_data = filter_non_null(
        facebook_data, facebook_data_columns_of_interest)
    google_data = filter_non_null(google_data, google_data_columns_of_interest)

    # Join website and facebook data on domain
    merged_data = pd.merge(website_data, facebook_data, left_on='root_domain',
                           right_on='domain', how='outer', suffixes=('_website', '_facebook'))

    # Separate Google data into unique and non-unique domains
    google_unique = google_data[google_data['domain'].duplicated(
        keep=False) == False]
    google_non_unique = google_data[google_data['domain'].duplicated(
        keep=False) == True]

    # Join the unique Google data on domain
    merged_data = pd.merge(merged_data, google_unique, left_on='root_domain',
                           right_on='domain', how='outer', suffixes=('', '_google_unique'))

    # First join non-unique Google data on name and country
    merged_data = pd.merge(merged_data, google_non_unique, left_on=['root_domain', 'site_name', 'main_country', 'main_city'], right_on=[
                           'domain', 'name', 'country_name', 'city'], how='left', suffixes=('', '_google_non_unique_reliable'))

    # Identify records that were not matched in the first join
    unmatched_google_non_unique = google_non_unique[~google_non_unique.index.isin(
        merged_data.index)]

    # Second join unmatched non-unique Google data on name only
    merged_data = pd.merge(merged_data, unmatched_google_non_unique, left_on=['root_domain', 'site_name', 'main_city'], right_on=[
                           'domain', 'name', 'city'], how='outer', suffixes=('', '_google_non_unique_less_reliable'))

    # Rename columns of interest to a more standardized format for easier processing
    merged_data.rename(columns={
        'site_name': 'name_website',
        'name': 'name_facebook',
        'address': 'address_google_unique',
        'phone': 'phone_google_unique',
        's_category': 'category_website',
        'categories': 'category_facebook',
        'category': 'category_google_unique'
    }, inplace=True)

    print('Reached resolved conflict stage')

    columns_to_resolve = ['category', 'address']
    resolved_data = merged_data.apply(
        resolve_conflict, axis=1, columns=columns_to_resolve)

    # Handle name and phone with prioritization
    resolved_name_phone = merged_data.apply(resolve_name_phone, axis=1)

    final_data = pd.concat(
        [merged_data, resolved_data, resolved_name_phone], axis=1)

    needed_columns = ['root_domain', 'domain', 'domain_google_unique', 'domain_google_non_unique_reliable',
                      'domain_google_non_unique_less_reliable', 'category', 'address', 'name', 'phone']

    result = final_data[needed_columns]

    # Check if directory of the output file exists
    # If not, create it and write the file in it
    output_dir = 'out'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = os.path.join(output_dir, 'company_data.xlsx')

    result.to_excel(output_file_path, index=False)
    print('SUCCESS!')


if __name__ == '__main__':
    main()