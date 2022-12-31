#Libraries
import pandas as pd
import numpy as np

#%%Load data
taped = pd.read_csv('TAPED_2.csv', sep = ';')
taped.describe().T

#%%Preprocess the data to the correct format (bilateral dataset)
#Select key columns
taped = taped[['taped_number','long_title', 'short_title', 'type ', 'parties', 'date_signed', 'year_signed', 'date_into_force', 'withdrawals', 'language', 'data_prot_prov_2_1_1', 'data_free_flow_prov_2_2_1', 'data_flow_free_mov_outside2_3_1']]

#Remove special characters
taped.parties = taped.parties.str.replace(';', ',', regex=True)
taped.parties = taped.parties.str.replace('(', '', regex= True)
taped.parties = taped.parties.str.replace(')', '', regex = True)
taped.parties = taped.parties.str.replace('EFTA', 'CHE, ICE, NOR, LIE', regex= True)
taped.parties = taped.parties.str.replace('MERCOSUR', 'ARG, BRA, PRY, URY', regex=True)
taped.parties = taped.parties.str.replace('ASEAN', 'BRN, IDN, KHM, LAO, MYS, MMR, THA, PHL, SGP, VNM', regex = True)
taped.parties = taped.parties.str.replace('SADEC', 'AGO, BWA, COD, SWZ, LSO, MDG, MWI, MUS, MOZ, NAM, SYC, ZAF, TZA', regex= True)
taped.parties = taped.parties.str.replace('SAFTA', 'AFG, BGD, BTN, IND, NPL, MDV, PAK, LKA', regex=True)
taped.parties = taped.parties.str.replace('CARICOM', 'ATG, BHS, BRB, BLZ, DMA, GRD, GUY, HTI, JAM, MSR, KNA, LCA, VCT, SUR, TTO', regex = True)
taped.parties = taped.parties.str.replace('CARIFORUM', 'ATG, BHS, BRB, BLZ, DMA, GRD, GUY, JAM, LCA, VCT, KNA, SUR, TTO, DOM', regex = True)

df = taped.parties.apply(lambda x: pd.Series(str(x).split(",")))
df.rename(columns={0: 'party_1', 1: 'party_2', 2: 'party_3', 3: 'party_4', 
4: 'party_5', 5: 'party_6', 6: 'party_7', 7: 'party_8', 8: 'party_9', 9: 'party_10', 10: 'party_11', 11: 'party_12', 12: 'party_13', 13: 'party_14', 14: 'party_15', 15: 'party_16', 16: 'party_17', 17: 'party_18', 18: 'party_19', 19: 'party_20', 
20: 'party_21', 21: 'party_22', 22: 'party_23', 23: 'party_24', 24: 'party_25', 25: 'party_26'}, inplace= True)

# Create List of columns
col_list= ['party_1', 'party_2', 'party_3', 'party_4', 'party_5', 'party_6',
       'party_7', 'party_8', 'party_9', 'party_10', 'party_11', 'party_12',
       'party_13', 'party_14', 'party_15', 'party_16', 'party_17', 'party_18',
       'party_19', 'party_20', 'party_21', 'party_22', 'party_23', 'party_24',
       'party_25', 'party_26']
merged = pd.merge(taped, df, how = 'left', left_index= True, right_index= True)

#Melt dataframe
keys = [c for c in merged if c.startswith('party_')]
melted_df = pd.melt(merged, id_vars='short_title', value_vars=keys, value_name='key').drop_duplicates()

#Merge
final_df = pd.merge(melted_df, taped, how = 'left', on = 'short_title')
final_df.sort_values(by = ['short_title', 'key'])

#drop irrelevant information in columns
final_df.drop(['parties', 'date_signed', 'withdrawals', 'type ', 'language'], axis=1, inplace= True)

#drop NAs
final_df = final_df.dropna(subset= ['short_title'])
final_df = final_df.dropna(subset = 'key')


#Create variable of data agreement (if it contains either data localization, data cross border transfer (within digital trade chapter or outside), data clauses in other chapters, or reference to data innovation)

final_df['RTA_data_clause'] = 0

final_df.loc[((final_df['data_prot_prov_2_1_1'] > 0) | (final_df['data_free_flow_prov_2_2_1'] > 0) | (final_df['data_flow_free_mov_outside2_3_1'] > 0)), 'RTA_data_clause'] = 1

#Create variable that says whether the RTA contains a data protection clause
final_df['RTA_data_prot'] = 0
final_df.loc[(final_df['data_prot_prov_2_1_1'] > 0), 'RTA_data_prot'] = 1

#Create variable that indicates whether the RTA contains a cross border data 
final_df['RTA_data_cross'] = 0
final_df.loc[(final_df['data_free_flow_prov_2_2_1'] > 0) | (final_df['data_flow_free_mov_outside2_3_1'] > 0), 'RTA_data_cross'] = 1

#%%Join dataframe onto itself by trade agreement unique number (taped number)
copy_df = final_df.copy()
joined = pd.merge(final_df, copy_df, on = 'taped_number', how= 'left')

#Adapt the column names
joined.rename(columns={'short_title_x': 'RTA_data_name_short', 'long_title_x': 'RTA_data_name_long', 'year_signed_x': 'year_signed', 'date_into_force_x': 'date_into_force', 'key_x': 'country_i', 'key_y': 'country_j', 'RTA_data_clause_x': 'RTA_data_clause','RTA_data_prot_x' : 'RTA_data_prot', 'RTA_data_cross_x': 'RTA_data_cross'}, inplace=True)

#Keep only relevant columns
joined = joined.loc[:,['taped_number','RTA_data_name_short','RTA_data_name_long', 'country_i', 'country_j', 'year_signed', 'date_into_force','RTA_data_clause', 'RTA_data_prot', 'RTA_data_cross']]

# Drop the duplicate rows
duplicate_rows = joined[joined['country_i'] == joined['country_j']]
joined_2 = joined.drop(duplicate_rows.index).reset_index()

joined_2 = joined_2.sort_values(by = ['taped_number'])

#Drop all instances where no data clause was initiated
filtered = joined_2[joined_2['RTA_data_clause'] ==1]
filtered.to_csv('test.csv')

# %% Create time dimension

#Create 21 duplicates of the original dataframe
duplicated_dfs = [filtered.copy() for _ in range(21)]

# Concatenate all of the duplicated dataframes into a single dataframe
result_df = pd.concat(duplicated_dfs)

#Sort by indices
result_df.sort_values(by = ['taped_number', 'country_i', 'country_j'], inplace=True)

#fill up a new year column with the years needed from 2000 to 2021
result_df['year'] = len(filtered) * list(range(2000, 2021))
result_df['RTA_data'] = (result_df.year > result_df.year_signed) * result_df.RTA_data_clause

result_df['RTA_data_prot_clause'] = (result_df.year > result_df.year_signed) * result_df.RTA_data_prot

result_df['RTA_data_cross_clause'] = (result_df.year > result_df.year_signed) * result_df.RTA_data_cross

result_df = result_df.rename(columns= {'country_i': 'iso3_i', 'country_j': 'iso3_j'})

result_df = result_df[['iso3_i','iso3_j', 'year', 'RTA_data', 'RTA_data_prot_clause', 'RTA_data_cross_clause']]

result_df.to_csv('RTA_data.csv')
# %% Test dataframe

