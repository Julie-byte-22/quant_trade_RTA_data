#Libraries
import pandas as pd
import numpy as np
#%%Load data
itc = pd.read_csv('./ITC_data/ITPD_E_R02.csv')
itc.describe().T

#%%Filter data needed
year_start = 2000
year_end = 2019
filtered_df = itc[(itc['year'] >= year_start) & (itc['year'] <= year_end)]

#%%
#result = filtered_df[filtered_df['exporter_iso3'] == filtered_df['importer_iso3']]

res = filtered_df.groupby(by = ['exporter_iso3', 'importer_iso3', 'year'], as_index=False).agg(
    {'trade': 'sum'})

res = res.rename(columns = {'exporter_iso3': 'iso3_i', 'importer_iso3': 'iso3_j'})

res.to_csv('ITC_data.csv')
#%%