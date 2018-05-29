#function to compute the crowd density at dfferent times
import pandas as pd
import numpy as np	#Because I a like it
import matplotlib.pyplot as plt

chunksize=10000
maxp=20
tarid=9384600
init=1
date='20121125'
tp = pd.read_csv('/usr/atc-dataset/atc-'+date+'.csv', header=None, iterator=True, chunksize=chunksize, low_memory=False)
i=0	#ineration number
timestamp=float(0)
last_timestamp=float(-1)
finish=0 #did we finish searching?
density_arr= np.empty((0,2), dtype=float)
skip=0
skip_size=0
count=0

for gm_chunk in tp:
	#Initialization
	#Don't do anything except load during initialization
	if init==1:
		init=0
		data=gm_chunk.values[:,0]
		tstart=data[0]	#time at the first reading. Will be used to remove offset
		data-=tstart	#remove time offset
		timestamp=0
		continue

	#skip skip_size chunks
	if skip:
		if count<skip_size:
			count+=1
			continue
		skip=0
		count=0
	#Not init
	last_data=data
	data=gm_chunk.values[:,0]
	data-=tstart	#remove time offset
	
	#look for new timestamp
	j=0
	while timestamp==last_timestamp and j<chunksize:
		timestamp=last_data[j]
		j+=1

	#Skip if new timestamp couldn't be found
	if timestamp==last_timestamp:
		continue

	#combine 2 chunks
	arr=np.concatenate((last_data,data),axis=0)
	skip=1
	
	nump=np.sum(arr==timestamp)
	#print(density_arr)
	#print([timestamp,arr])
	density_arr=np.concatenate((density_arr,[[timestamp,nump]]),axis=0)
	last_timestamp=timestamp
	print(timestamp)

fig = plt.figure()
ax = plt.subplot(111)
ax.plot(density_arr[:,0], density_arr[:,1], label='$y = No. of people')
plt.title('Crowd')
ax.legend()
fig.savefig(date+'-plot.png')