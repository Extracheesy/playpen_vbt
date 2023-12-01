import pandas as pd

# Assuming df1 is the first dataframe with hourly samples and 'value' column
# Assuming df2 is the second dataframe with capital values at specific dates

# Create the first dataframe
date_rng = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
df1 = pd.DataFrame(date_rng, columns=['date'])
df1['value'] = 1000

# Create the second dataframe
dates = ['2023-01-01', '2023-06-01', '2023-11-01']
capital_values = [100, 500, 800]
df2 = pd.DataFrame({'date': pd.to_datetime(dates), 'capital': capital_values})

# Merge the dataframes based on the date column
df_merged = pd.merge_asof(df1, df2, on='date')

# Forward fill the 'capital' column to fill the NaN values
df_merged['capital'] = df_merged['capital'].ffill()

# Create the 'cpt' column based on the 'capital' values
df_merged['cpt'] = df_merged['capital']

# Drop the 'capital' column if needed
df_merged = df_merged.drop(columns=['capital'])

# Print or use the resulting dataframe df_merged
print(df_merged)