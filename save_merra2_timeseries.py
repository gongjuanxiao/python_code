#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Jessie Zhang, 08/06/2020
#save MERRA-2 model output into time series for all the sites
@author: huazhang
"""
import numpy as np
import math
import pandas as pd
import datetime 
import os, fnmatch, sys, re
import glob 
from datetime import datetime, timedelta
from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import ImageGrid
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes

def read_merra2_2d(file_data, var):
	
    # reading asm aer 2d data 
	nc = Dataset(file_data)
	var_data = nc.variables[var]
	
	var_data.set_auto_maskandscale(False)
	band_data = var_data[:,:,:].astype(np.float)
	
	# Retrieve attributes.
	scale_factor = var_data.scale_factor
	add_offset = var_data.add_offset
	_FillValue = var_data._FillValue
	valid_min = var_data.vmin
	valid_max = var_data.vmax 
	long_name = var_data.long_name
	units = var_data.units
	
	invalid = np.logical_or(band_data > valid_max, band_data < valid_min)
	invalid = np.logical_or(invalid, band_data == _FillValue)
	band_data[invalid] = np.nan 
	band_data = (band_data - add_offset) * scale_factor
	band_data = np.ma.masked_array(band_data, np.isnan(band_data))
	
	nc.close()
	return band_data
	
def read_merra2_latlon(file_data):

   # opening file and reading interest variable without scaling etc. 
   nc = Dataset(file_data)
   lat_data = nc.variables['lat'][:]
   lon_data = nc.variables['lon'][:]

   nc.close()

   return lat_data, lon_data
   
######################################################
# main program begins here
######################################################

#geting merra-2 lat and lon info

#directory for MERRA-2 data 
dir_merra2  = './'
#use the pattern to search file
pattern = 'MERRA2_400.tavg1_2d_lnd_Nx.*0301*'
list_raw = fnmatch.filter(os.listdir(dir_merra2),pattern)
filelist = np.sort(list_raw)

print ('files found are :', filelist)
###### read one file to get lat and lon info #######
filename = dir_merra2 + filelist[0]
lat_merra2, lon_merra2 = read_merra2_latlon(filename)
#mesh the lat and lon grid for plotting 
lon_merra2_2d, lat_merra2_2d = np.meshgrid(lon_merra2,lat_merra2)
#zip them together
merra2_dim = lon_merra2_2d.shape


############################################################
# read ground sites info and corresponding MERRA-2 index
############################################################

list_site_info = './MERRA2_index.csv'

#reading the csv file
df = pd.read_csv(list_site_info, dtype = object)
#print(df)
#data_ext = df[['siteID', 'sitelat', 'sitelon', 'MERRA2lati', 'MERRA2lonj']]]data_ext = df[['siteID', 'sitelat', 'sitelon', 'MERRA2lati', 'MERRA2lonj']]
data_ext = df[[ 'sitelat', 'sitelon', 'MERRA2lati', 'MERRA2lonj']]
#mask = (data_ext['sitelat'].astype(float) >= minlat) & (data_ext['sitelat'].astype(float) <= maxlat) & (data_ext['sitelon'].astype(float) >= minlon) & (data_ext['sitelon'].astype(float) <= maxlon)
#data_ext2 = data_ext[mask]

#list_siteid = data_ext2['siteID'].values
list_sitelat = data_ext['sitelat'].values.astype(float)
list_sitelon = data_ext['sitelon'].values.astype(float)
list_site_wlatind = data_ext['MERRA2lati'].values.astype(int)
list_site_wlonind = data_ext['MERRA2lonj'].values.astype(int)

########################################################
# extract variables (saving PM2.5)
##########################################################
'''
convert 		= lambda text: int(text) if text.isdigit() else text
alphanum_key 	= lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

wrf_files = glob.glob(dir_asm_aer + 'MERRA2_400.tavg1_2d_aer_Nx.*')
#print('wrf file list is:', wrf_files)
wrf_files.sort(key=alphanum_key)
#print('wrf file list after sorting is:', wrf_files)

#define start and end time series to plot or save the timeseries data
begin_serie = pd.Timestamp(year=2018, month=03, day=01, hour=0)
end_serie = pd.Timestamp(year=2018, month=03, day=01, hour=23)
'''


#create a date range for extracting data 
time_sim = pd.date_range(start='2018-03-01', end='2018-03-01', freq='D')
#of days 
n_day = len(time_sim)

#create a empty dataframe for saving data 
df_temp = pd.DataFrame(columns=[])

#surface moisture in m3/m3
var = ['SFMC']

pattern1='MERRA2_400.tavg1_2d_lnd_Nx.'

#loop through the day
for d in np.arange(0, n_day):
#for i in np.arange(0, 1):

	#convert the date object to string for pattern searching
	date_str =  time_sim[d].strftime('%Y%m%d')
	print ('date str is:', date_str)
	
	result1 = fnmatch.filter(os.listdir(dir_merra2), pattern1 + date_str+ '*')
	
	if len(result1) > 0:
		
		sm = read_merra2_2d(dir_merra2 + result1[0],var[0])

		for h in np.arange(0,24):
		
			# adding each hour to each day for saving data 
			time_date_update = time_sim[d] + timedelta(hours=int(h))
			print('time_date_update is:', time_date_update)
						
			df_temp = df_temp.append(pd.Series([np.nan]), ignore_index = True)
			row = len(df_temp)
			df_temp.loc[row-1, 'timestamp'] = time_date_update
		
			if sm.size > 0:
		
				for idx, id_site in enumerate(list_sitelat):
					col_name = str(idx)
					df_temp.loc[row-1, col_name] = sm[h,list_site_wlatind[idx], list_site_wlonind[idx]]
			


		
#print(df_temp)
df_temp=df_temp.drop(0,1)

#######save SM data #############
df_temp.to_csv("./TS_merra2_sm.csv",na_rep='NaN', index=False)


#'''
	
