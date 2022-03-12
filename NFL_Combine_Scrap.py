import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Import scraping tools
import requests
from bs4 import BeautifulSoup

list_1 = []

for year in range(1987,2022):
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
    print(year)

# Create DataFrame from data:
combine_df = pd.DataFrame(list_1, columns = header)

combine_df.tail()

## Find data types:
combine_df.info()

# Convert numeric data

combine_df['Height (in)'] = combine_df['Height (in)'].astype(float)
combine_df['Weight (lbs)'] = combine_df['Weight (lbs)'].astype(float)
combine_df['40 Yard'] = combine_df['40 Yard'].astype(float)
combine_df['Vert Leap (in)'] = combine_df['Vert Leap (in)'].astype(float)
combine_df['Broad Jump (in)'] = combine_df['40 Yard'].astype(float)
combine_df['Shuttle'] = combine_df['Shuttle'].astype(float)
combine_df['3Cone'] = combine_df['3Cone'].astype(float)
combine_df['Bench Press'] = combine_df['Bench Press'].astype(int)