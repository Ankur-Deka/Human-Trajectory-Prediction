#Collects data from ATC atset within the given spatial range and converts it for compatibility with social attention code

import pandas as pd
import numpy as np
import os
import argparse
import time

parser=argparse.ArgumentParser()
parser.add_argument('-l','--list', nargs='+', help='<Required> Spatial range to collect data from : xmin xwidth ymin ywidth', default=[-3,6,-3,6], type=float)
# Use like:
# python transpose_inrange.py -l xmin xmax ymin ymax
args=parser.parse_args()
[xmin,xwidth,ymin,ywidth]=args._get_kwargs()[0][1]
xmax=xmin+xwidth
ymax=ymin+ywidth

chunksize=10000
num_chunks=1
date='20121121'
tp = pd.read_csv('/usr/atc-dataset/atc-'+date+'.csv', header=None, iterator=True, chunksize=chunksize, low_memory=False)

i=0
arr_full=np.empty((4,0),dtype=float)

for gm_chunk in tp:
	if i==num_chunks:	#use only mentioned number of chunks 
		break
	print('Reading Chunk no.:',i)

	data=gm_chunk.values[:,0:4].transpose()
	#data[0,:]=data[0,:]*100
	data[[2,3],:]/=1000
	
	arr_full=np.append(arr_full,data,axis=1)
	i+=1
print('Done reading chunks')

#create directory if doesn't exist
os.makedirs(date, exist_ok=True)

#Remove columns outside spatial range
arr_full=arr_full[:,np.where(arr_full[2,:]>xmin)[0]]
arr_full=arr_full[:,np.where(arr_full[2,:]<xmax)[0]]
arr_full=arr_full[:,np.where(arr_full[3,:]>ymin)[0]]
arr_full=arr_full[:,np.where(arr_full[3,:]<ymax)[0]]
print('arr_full.shape',arr_full.shape,'\n')

#Convert timestamps and personIDs are incrementing natural numbers
arr_full[0,:] = pd.factorize(arr_full[0,:])[0]+1	#timestamp conversion. Crude because all timestamps are considered equal.
arr_full[1,:] = pd.factorize(arr_full[1,:])[0]+1

#Change IDs for pedestrians who went out and came back
org_maxID=max(arr_full[1,:])
maxID=org_maxID

ID=1
while(ID<=maxID):
	print('Checking ID',ID)
	pos_arr=np.where(arr_full[1,:]==ID)[0]		#positions where ID is present
	time_arr=arr_full[0,pos_arr]	#time instances where that ID is present
	diff_arr=(np.concatenate((time_arr,[0]),axis=0)-np.concatenate(([0],time_arr),axis=0))[1:-1]	#difference array
	miss_tpos_arr=np.where(diff_arr!=1)[0]	#array of missing positions (time after which it went missing) in the time_arr. These are not positions in actual array butpositions in time_arr
	#print('time_arr',time_arr)
	if(miss_tpos_arr.any()):
		print('missing times-1',time_arr[miss_tpos_arr])
		#sequentially solve for each missing position deaing with only the minimum
		miss_time=min(time_arr[miss_tpos_arr])
		miss_pos=min(np.where(arr_full[0,:]>miss_time)[0])	#actual missing position in array
		
		pos_change_arr=pos_arr[pos_arr>=miss_pos]	#array of positions where ID needs to be changed
		arr_full[1,pos_change_arr]=maxID+1
		maxID=maxID+1
	ID+=1	#move to next ID
	#ime.sleep(0.5)
#AGAIN
#Convert timestamps and personIDs are incrementing natural numbers
arr_full[0,:] = pd.factorize(arr_full[0,:])[0]+1	#timestamp conversion. Crude because all timestamps are considered equal.
arr_full[1,:] = pd.factorize(arr_full[1,:])[0]+1

np.savetxt(date+'/pixel_pos_interpolate.csv',arr_full[[0,1],:].astype(int),delimiter=',',fmt='%i')
with open(date+'/pixel_pos_interpolate.csv','a') as f_handle:
    np.savetxt(f_handle,arr_full[[2,3],:],delimiter=',')