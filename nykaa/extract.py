import pandas as pd

# Load the original CSV file
input_file = 'nykaa_categories.csv'  # Replace with the actual file name
df = pd.read_csv(input_file)

# Create a unique combination of category, subcategory, and product type
unique_categories = df[['Category', 'Subcategory', 'Product Type']].drop_duplicates().reset_index(drop=True)

# Add a unique category ID
unique_categories['CategoryId'] = range(1, len(unique_categories) + 1)

# Save the unique categories to a new CSV file
unique_categories_csv = 'unique_categories.csv'
unique_categories.rename(columns={
    'Category': 'Category1',
    'Subcategory': 'Category2',
    'Product Type': 'Category3'
}, inplace=True)
unique_categories = unique_categories[['CategoryId', 'Category1', 'Category2', 'Category3']]
unique_categories.to_csv(unique_categories_csv, index=False)

# Merge the original data with the unique categories to get the CategoryId
merged_df = df.merge(unique_categories, left_on=['Category', 'Subcategory', 'Product Type'], 
                     right_on=['Category1', 'Category2', 'Category3'])

# Drop the original category columns and keep the rest
final_data = merged_df.drop(columns=['Category', 'Subcategory', 'Product Type', 'Category1', 'Category2', 'Category3'])

# Reorder columns to make CategoryId the first column
columns = ['CategoryId'] + [col for col in final_data.columns if col != 'CategoryId']
final_data = final_data[columns]

# Save the final data to another CSV file
final_data_csv = 'final_data.csv'
final_data.to_csv(final_data_csv, index=False)

print(f"Unique categories saved to {unique_categories_csv}")
print(f"Final data saved to {final_data_csv}")