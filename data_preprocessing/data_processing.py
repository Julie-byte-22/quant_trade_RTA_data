#Libraries
import pandas as pd
import numpy as np

#%%
#Load data
gravity_data = pd.read_csv('gravity_original.csv', index_col=0)
gravity_data.describe().T

itc = pd.read_csv('itc_data.csv')
itc_filtered = itc.loc[itc['iso3_i']==itc['iso3_j'], :].copy()
itc_filtered = itc_filtered[['iso3_i', 'iso3_j', 'trade', 'year']]

taped = pd.read_csv('RTA_data.csv', index_col=0)
taped = taped.reset_index()
taped.iso3_i = taped.iso3_i.apply(lambda x: x.strip(' '))
taped.iso3_j = taped.iso3_j.apply(lambda x: x.strip(' '))

#%%Concat gravity data and itc data
gravity_data_fin = pd.concat([gravity_data, itc_filtered])

#Create helper dictionary for gdp
gdp_df = gravity_data[['iso3_i', 'year', 'gdp_i', 'pop_i']].drop_duplicates()

def my_function(x):
    if x.iso3_i == x.iso3_j:
        x.dist = 0
        x.rta = 0
        x.col = 1
        x.contig = 0
        x.comcol = 0
        a = gdp_df.loc[(gdp_df['iso3_i']==x.iso3_i) & 
                       (gdp_df['year']==x.year), :].head(1)
        if (a.shape[1]==gdp_df.shape[1]) and (a.shape[0]==1):
            x.gdp_i = a.gdp_i.to_numpy()[0]
            x.pop_i = a.pop_i.to_numpy()[0]
        x.gdp_j = x.gdp_i
        x.pop_j = x.pop_i
    return x

gravity_data_fin = gravity_data_fin.apply(my_function, axis = 1)

# gravity_data_fin.to_csv('gravity_final.csv')
#%%

gravity_data_fin = gravity_data_fin.reset_index()
taped = taped.reset_index()

gravity_data_fin['iso3_i'] = gravity_data_fin['iso3_i'].astype(str)
gravity_data_fin['iso3_j'] = gravity_data_fin['iso3_j'].astype(str)

#Merge gravity_data and taped
result = pd.merge(gravity_data_fin, taped, on=['iso3_i', 'iso3_j', 'year'], how='left')

result['RTA_data'] = result['RTA_data'].fillna(0)
result['RTA_data_prot_clause'] = result['RTA_data_prot_clause'].fillna(0)
result['RTA_data_cross_clause'] = result['RTA_data_cross_clause'].fillna(0)

#Restrict years 2010-2019
result = result[result['year'] > 2009]

#Restrict countries to OECD countries
OECD = ['FRA','DEU', 'ITA', 'USA', 'GBR', 'NOR', 'SWE', 'AUS', 'AUT', 'BEL',
'CAN', 'CZE', 'EST', 'DNK', 'CHL', 'FIN', 'GRC', 'HUN', 'ISL', 'IRL' , 'ISR', 'JPN', 'PRT', 'SVK', 'SVN', 'ESP', 'CHE', 'TUR', 'COL', 'CRI', 'KOR', 'LVA', 'LUX', 'LTU','NZL', 'MEX', 'NLD', 'POL']

def check_OECD_pair(x):
    return (x.iso3_i in OECD) and (x.iso3_j in OECD) 

def check_OECD(x):
    return (x.iso3_i in OECD)

oecd_asia = ['FRA','DEU', 'ITA', 'USA', 'GBR', 'NOR', 'SWE', 'AUS', 'AUT', 'BEL', 'CAN', 'CZE', 'EST', 'DNK', 'CHL', 'FIN', 'GRC', 'HUN', 'ISL', 'IRL' , 'ISR', 'JPN', 'PRT', 'SVK', 'SVN', 'ESP', 'CHE', 'TUR', 'COL', 'CRI', 'KOR', 'LVA', 'LUX', 'LTU','NZL', 'MEX', 'NLD', 'POL', 'IND', 'CHN', 'JPN', 'KOR', 'TWN', 'BRN', 'IDN', 'KHM', 'LAO', 'MYS', 'MMR', 'THA', 'PHL', 'SGP', 'VNM']

def check_OECD_ASIA_pair(x):
    return (x.iso3_i in oecd_asia) and (x.iso3_j in oecd_asia) 

result['is_OECD_pair'] = result.apply(check_OECD_ASIA_pair, axis=1)
result = result.loc[result['is_OECD_pair'], :].copy()

#Create pairid 
result['pair_id'] = (result['iso3_i'] + '_' + result['iso3_j']).astype('category').cat.codes

#Drop columns and duplicate values
result = result.drop(columns={'index_x', 'level_0', 'index_y', 'is_OECD_pair', 'gdp_i', 'gdp_j', 'pop_i', 'pop_j'})
result = result.sort_values(['iso3_i', 'iso3_j', 'year']).drop_duplicates(subset=['iso3_i', 'iso3_j', 'year'])

#Write final dataframe to stata
result.to_csv('gravity_final_OECD_ASIA.csv', index = False)
