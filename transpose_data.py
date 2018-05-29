import pandas as pd
import numpy as np
import os

chunksize=2000
num_chunks=1
date='20121125'
tp = pd.read_csv('/usr/atc-dataset/atc-'+date+'.csv', header=None, iterator=True, chunksize=chunksize, low_memory=False)

i=0
arr_full=np.empty((4,0),dtype=float)

for gm_chunk in tp:
	if i==num_chunks:	#use only mentioned number of chunks 
		break
	print(i)

	data=gm_chunk.values[:,0:4].transpose()
	#data[0,:]=data[0,:]*100
	data[[2,3],:]/=1000
	
	arr_full=np.append(arr_full,data,axis=1)
	print(arr_full.shape)
	i+=1

#create directory if doesn't exist
os.makedirs(date, exist_ok=True)

arr_full[0,:] = pd.factorize(arr_full[0,:])[0]+1
arr_full[1,:] = pd.factorize(arr_full[1,:])[0]+1
np.savetxt(date+'/pixel_pos_interpolate.csv',arr_full[[0,1],:].astype(int),delimiter=',',fmt='%i')


with open(date+'/pixel_pos_interpolate.csv','a') as f_handle:
    np.savetxt(f_handle,arr_full[[2,3],:],delimiter=',')