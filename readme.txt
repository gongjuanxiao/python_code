#Jessie Zhang, uiowa, 08/06/20120

1) Please follow the instructions from this link:https://disc.gsfc.nasa.gov/data-access#mac_linux_wget to 
   create an Earthdata account (if you do not have one) to download MERRA-2 data.

2) MERRA-2 data are organized by collections. The collection that saves land-related diagnostics is MERRA2 tavg1_2d_lnd_Nx (M2T1NXLND)
   You can download a MERRA-2 file specification document for more information about the variables. I also attached a MERRA land product
   .pdf which includes some informationa about soil moisture. 

3) using python code find_index.py to find the index info of the ground site in MERRA-2 or other model grid. 
   this will make extracting data easier.

4) using python code save_merra2_timeseries.py to save the MERRA-2 soil moisture data for each site into a time series format