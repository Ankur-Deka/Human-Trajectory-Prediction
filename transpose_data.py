import pandas as pd
import numpy as np
import os

chunksize=10000
num_chunks=1
date='20121121'
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
	i+=1

#create directory if doesn't exist
os.makedirs(date, exist_ok=True)

#Convert timestamps and personIDs are incrementing natural numbers
arr_full[0,:] = pd.factorize(arr_full[0,:])[0]+1	#timestamp conversion. Crude because all timestamps are considered equal.
arr_full[1,:] = pd.factorize(arr_full[1,:])[0]+1

#Crude interpolation assuming timesteps are of equal length
ID_arr=np.unique(arr_full[1,:])	#get all the the person IDs. After this, I'll mean person ID when I say ID
#Now we will run check and interpolate for each person in ID_arr
err_list=[]
size_list=[]
for ID in ID_arr:
	time_arr=arr_full[0,np.where(arr_full[1,:]==ID)]	#time instances where that ID is present
	time_arr=time_arr.reshape(time_arr.shape[1])
	if(time_arr.shape!=time_arr[-1]-time_arr[0]+1):
		err_list.append(ID)
		diff_arr=(np.concatenate((time_arr,[0]),axis=0)-np.concatenate(([0],time_arr),axis=0))[1:-1]	#difference array
		print(diff_arr)
		miss_pos=np.where(diff_arr!=1)[0]
		#size_list.append(len(miss_pos[0]))
		print('miss_pos',miss_pos)
		for pos in miss_pos:	#go through all the missing positions
			print('pos',pos)
			miss_time=int(time_arr[pos])	#time after which person went missing
			found_time=int(time_arr[pos+1])	#time when person was found after lost
			for t in range(miss_time+1,found_time):	#we need to fiil for the time in between
				x=np.interp(t,[miss_time,found_time],arr_full[2,[miss_time,found_time]])	#use numpy to perform linear interpolation
				y=np.interp(t,[miss_time,found_time],arr_full[3,[miss_time,found_time]])
				data=np.asarray([[t],[ID],[x],[y]])		#create the column to be inserted
				ins_pos=np.min(np.where(arr_full[0,:]==t))	#find the position where it is to be inserted
				
				arr_full=np.insert(arr_full,[ins_pos],data,axis=1)	#insert it


#Visualize if we filled in correctly
print(err_list)
print('hi',size_list,'hi')
for ID in err_list:
	time_arr=arr_full[0,np.where(arr_full[1,:]==ID)]	#time instances where that ID is present
	time_arr=time_arr.reshape(time_arr.shape[1])
	diff_arr=(np.concatenate((time_arr,[0]),axis=0)-np.concatenate(([0],time_arr),axis=0))[1:-1]	#difference array
	print(np.where(diff_arr!=1))


np.savetxt(date+'/pixel_pos_interpolate.csv',arr_full[[0,1],:].astype(int),delimiter=',',fmt='%i')
with open(date+'/pixel_pos_interpolate.csv','a') as f_handle:
    np.savetxt(f_handle,arr_full[[2,3],:],delimiter=',')