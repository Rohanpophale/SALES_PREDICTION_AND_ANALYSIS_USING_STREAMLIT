import pandas as pd

# Load the random_value.csv dataset
df = pd.read_csv('CSV_Files/JustDial_sales_data.csv')

# Define a function to normalize a column
def normalize_column(column):
    min_val = column.min()
    max_val = column.max()
    normalized_column = (column - min_val) / (max_val - min_val)
    return normalized_column

# Specify the columns you want to normalize
columns_to_normalize = ['total_active', 'paid', 'non_paid', 'paid_expired', 'geocoded', 'building_level', 'landmark_level', 'non_geocoded']

# Normalize the selected columns
for column in columns_to_normalize:
    df[column] = normalize_column(df[column])

# Save the normalized dataset to a new CSV file
df.to_csv('CSV_Files/Normalized_JustDial_sales_data.csv', index=False)
