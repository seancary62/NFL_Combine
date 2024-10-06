###### SCRAPE AND TRANSIFORM DATA FOR THE DASHBOARD ######
# Code from the NFL_Combine_Scrap and NFL_Combine_Transform_Explore 
# is refractored here. This script can be scheduled to run yearly
# To update the results.

# Import libraries
import numpy as np 
import pandas as pd 
from datetime import datetime

# Import scraping tools
import requests
from bs4 import BeautifulSoup

# Import sklearn
from sklearn.preprocessing import MinMaxScaler

current_year = datetime.now().year

list_1 = []

for year in range(1987,current_year+1):
    # Get the URL
    url = f'https://nflcombineresults.com/nflcombinedata.php?year={year}&pos=&college='

    # Make the request
    r = requests.get(url)

    # Parse the script
    soup = BeautifulSoup(r.text, 'html.parser')
    

    # Pull the table data

    combine_table = soup.find('table', class_='sortable')
    
    # Get header from first year.
    if (year == 1987):
        # Get the table header
        header = []
        for title in combine_table.find_all('thead'):
            rows = title.find_all('tr')
            for row in rows:
                for i in range(13):
                    pl_data = row.find_all('td')[i].text.strip()
                    header.append(pl_data)
    
    
    # Get player data
    for player in combine_table.find_all('tbody'):
        rows = player.find_all('tr')
        for row in rows:
            list_2 = []
            for i in range(13):
                pl_data = row.find_all('td')[i].text.strip()
                list_2.append(pl_data)
            list_1.append(list_2)
    
    #Track progress
    if year % 5 == 0:
        print(f'Just completed the year: {year}')
    elif year == current_year:
        print(f'Just completed final year: {year}')


# Create DataFrame from data:
combine_df = pd.DataFrame(list_1, columns = header)

# Convert datatypes for processing and convert missing vales to NaN so that they will not be counted in the analysis
combine_df['Height (in)'] = combine_df['Height (in)'].astype(float)
combine_df['Weight (lbs)'] = combine_df['Weight (lbs)'].astype(float)
combine_df['40 Yard'] = combine_df['40 Yard'].replace('',np.nan, regex=True).astype(float)
combine_df['Vert Leap (in)'] = combine_df['Vert Leap (in)'].replace('',np.nan, regex=True).astype(float)
combine_df['Broad Jump (in)'] = combine_df['Broad Jump (in)'].replace('',np.nan, regex=True).astype(float)
combine_df['Shuttle'] = combine_df['Shuttle'].replace('',np.nan, regex=True).astype(float)
combine_df['3Cone'] = combine_df['3Cone'].replace('',np.nan, regex=True).astype(float)
combine_df['Bench Press'] = combine_df['Bench Press'].replace('',np.nan, regex=True).astype(float)
combine_df['Wonderlic'] = combine_df['Wonderlic'].replace('',np.nan, regex=True).astype(float)

# Calculate BMI and add it to the combine dataframe
list_bmi = combine_df['Weight (lbs)'] / (combine_df['Height (in)'] ** 2) * 703

combine_df['BMI'] = list_bmi
combine_df.BMI = combine_df.BMI.round(1)

# Rearrange columns
cols = combine_df.columns.values

combine_df = combine_df[['Year', 'Name', 'College', 'POS', 'Height (in)', 'Weight (lbs)', 'BMI',
       'Wonderlic', '40 Yard', 'Bench Press', 'Vert Leap (in)',
       'Broad Jump (in)', 'Shuttle', '3Cone']]

#Drop Wonderlic due to NaN values and less relevent for our purposes
combine_df = combine_df.drop(['Wonderlic'], axis=1)

# Fix incorrect data from source
combine_df.loc[(combine_df['Name']=='Spencer Brown') & (combine_df['College']=='Alabama-Birmingham'), 'Bench Press'] = 16
combine_df.loc[(combine_df['Name']=='Jacoby Ford') & (combine_df['College']=='Clemson'), '40 Yard'] = 4.28
combine_df = combine_df.loc[(combine_df['Name'] != 'Trindon Holliday')]

# combine_df = pd.read_csv('resources/combine_df.csv')

###### CREATE A DATAFRAME FOR RECORD HOLDERS ######

combine_df_record = combine_df.copy()

# Get records for all combine data

record_stats_df = pd.DataFrame(
    [{"Max Height (in)":combine_df_record['Height (in)'].max(),
      "Max Weight (lbs)":combine_df_record['Weight (lbs)'].max(),
      "Max BMI":combine_df_record["BMI"].max(),
      "Min 40 Yard":combine_df_record['40 Yard'].min(),
      "Max Bench Press":combine_df_record['Bench Press'].max(), 
      "Max Vert Leap (in)":combine_df_record['Vert Leap (in)'].max(),
      "Max Broad Jump (in)":combine_df_record['Broad Jump (in)'].max(),
      "Min Shuttle":combine_df_record['Shuttle'].min(),
      "Min 3Cone":combine_df_record['3Cone'].min(),
    }])

# Transpose the dataframe:
record_stats_df_trans = record_stats_df.T
record_stats_df_trans.reset_index(inplace=True)
record_stats_df_trans.columns = ['Measure', 'Values']
record_stats_df_trans.Values = record_stats_df_trans.Values.round(2)

# Get all rows wth record holders

records_df = pd.DataFrame()
val_columns = combine_df_record.columns[4:]

for item in val_columns:
    try:
        if item == '40 Yard' or item =='Shuttle' or item =='3Cone':
            records_df = records_df.append(combine_df_record.loc[combine_df[item] == combine_df_record[item].min()])
        else:
            records_df = records_df.append(combine_df_record.loc[combine_df[item] == combine_df_record[item].max()])
    except:
        print('not a number column')

records_df.reset_index(drop=True,inplace=True)
records_df.drop(records_df.iloc[:,4:],inplace=True,axis=1)

# Combine transposed data with record holder data

records_players_df = records_df.merge(record_stats_df_trans,left_index=True,right_index=True)


###### CREATE A DATAFRAME WITH SCALED DATA ######
# This dataframe will be used for some visuals in
# PowerBI and determining the most well rounded
# athletes. It may also be used for machine learning.
combine_df_scale = combine_df.copy()

scaler = MinMaxScaler()

df_values = combine_df_scale.drop(['Name','Year','College','POS'], axis=1)
df_info = combine_df_scale.drop(['Height (in)', 'Weight (lbs)', 'BMI', '40 Yard', 'Bench Press', 'Vert Leap (in)', 'Broad Jump (in)', 'Shuttle', '3Cone'],axis=1)


df_scaled = scaler.fit_transform(df_values.to_numpy())
df_scaled = pd.DataFrame(df_scaled, columns=[
  'Height (in)', 'Weight (lbs)', 'BMI', '40 Yard', 'Bench Press', 'Vert Leap (in)', 'Broad Jump (in)', 'Shuttle', '3Cone'])
 
print("df values: ", df_values.shape)
print("df info: ", df_info.shape)
print("df scaled: ", df_scaled.shape)

df_info.reset_index(drop=True, inplace=True)
df_scaled.reset_index(drop=True, inplace=True)
combine_df_scaled = df_info.merge(df_scaled,left_index=True, right_index=True)

# Reverse order for speed measure so that faster times are the max
for col in ['40 Yard', 'Shuttle', '3Cone']:
    combine_df_scaled[col] = 1 - combine_df_scaled[col]


###### STORE THE DATA ######
combine_df.to_csv('resources/combine_df.csv', index=False)
combine_df_scaled.to_csv('resources/combine_df_scaled.csv', index=False)
records_players_df.to_csv('resources/records_players_df.csv', index=False)