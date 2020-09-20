#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Jessie Zhang, 08/06/2020
#this code will read the lat/lon info of ground stations; then it will find the index info of these station in the model grid
#this code will show an example of MERRA-2 model grid. it can be used for WRF-Chem model grid as well
@author: huazhang
"""
import numpy as np
import math
import pandas as pd
import datetime 
import os, fnmatch, sys, re
import glob 
from scipy import spatial
from datetime import datetime
from netCDF4 import Dataset

def read_merra2_latlon(filename):

   # opening file and reading interest variable without scaling etc. 
   nc = Dataset(filename)
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
merra2_grid = list(zip(np.ravel(lon_merra2_2d),np.ravel(lat_merra2_2d)))

####################################################
# read ground station info
####################################################
#directory for ground station data 

#note: I usually use pandas frame to read text file.
#here I show an example of readin text file. 
# somehow I cannot read the station file you shared correctly
# you can somehow resave that data and try here. 

'''
dir_ground = './'

list_sites_info = 'SouthFork Station Locations.txt'

#reading the csv file
df = pd.read_csv(dir_ground+list_sites_info, dtype=object)
print(df)


data_ext = df['Latitude','Longitude']
#mask = (data_ext['Latitude'].astype(float) >= minlat) & (data_ext['Latitude'].astype(float) <= maxlat) & (data_ext['Longitude'].astype(float) >= minlon) & (data_ext['Longitude'].astype(float) <= maxlon)
#data_ext2 = data_ext[mask]

#maybe to add a siteid to distinguish the sites

#list_siteid = data_ext2['siteid'].values
list_sitelat = data_ext['Latitude'].values.astype(float)
list_sitelon = data_ext['Longitude'].values.astype(float)

n_sites = len(list_sitelat)
print('# of sites: ', n_sites) 
'''


list_sitelat = [42.54262,42.4693]
list_sitelon = [-93.58906,-93.56545]

n_sites = len(list_sitelat)
print('# of sites: ', n_sites) 

######################################
# save sites info and its corresponding index in model grid into a text file
######################################
#name for the file

outfile_index = './MERRA2_index.csv'

# first check if the file exists 
if os.path.exists(outfile_index):
    print('file exists and delelte it now')
    os.remove(outfile_index)

data_out = pd.DataFrame(columns=['sitelat','sitelon','MERRA2lati','MERRA2lonj'])

count = 0
for i in np.arange(0,n_sites):
#for i in np.arange(0,1):
    
    target_pts = [list_sitelon[i],list_sitelat[i]]
    #find the nearest model grid and return the index 
    distance,index = spatial.KDTree(merra2_grid).query(target_pts)
    #print ('# of distances', distance)
    
    # the nearest model location (in lat and lon index)
    lonlat_ind = np.unravel_index(index, merra2_dim)
    #print ('latlon index is ', lonlat_ind)
     
    data_out = data_out.append([np.nan], ignore_index=True)
    #print ('save data', i)
    data_out.loc[count,['sitelat','sitelon','MERRA2lati','MERRA2lonj']]=[list_sitelat[i],list_sitelon[i], lonlat_ind[0], lonlat_ind[1]]
    count = count + 1
    print ('ground lat-lon and MERRA-2 lat-lon are:', list_sitelat[i],list_sitelon[i],lat_merra2_2d[lonlat_ind[0], lonlat_ind[1]], lon_merra2_2d[lonlat_ind[0], lonlat_ind[1]])

data_out=data_out.drop(0,1)
print (data_out)
data_out.to_csv(outfile_index,na_rep='NaN', index=False)
#'''
	
