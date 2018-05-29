#Update: velocity magnitude and direction instead of Vx and Vy
#Most likely, the start time of each file is the same. Remove timestamp offset
#Now take target_time (without offset) as input rather than target id
#introduce separate variable maxp_r and arrange the array. Sort by distance from target id
#Find way point and next point

import pandas as pd
import numpy as np	#Because I a like it
import matplotlib.pyplot as plt

chunksize=50
maxp=50		#max people in the file at a time
maxp_r=2
tarid=0
target_time=200
init=1
date='20121125'
tp = pd.read_csv('/usr/atc-dataset/atc-'+date+'.csv', header=None, iterator=True, chunksize=chunksize, low_memory=False)

delta_ip=1000	#delta given as input
rmin=1000.0
rmax=1000.0
m=int(np.ceil((rmax-rmin)/delta_ip))		#no. of spacings between radii, therefore no. of radii=m+1
if m!=0:
	delta=(rmax-rmin)/m 	#computed delta which is less than or equal to input delta
else:
	delta=0

#Function to normalize angle to the range (-pi,pi]
def norm_ang(theta):
	while(theta>np.pi):
		theta-=np.pi
	while(theta<=-np.pi):
		theta+=np.pi
	return theta

i=0	#ineration number
found=0	#checks if found till now
count=0	#Count how many continuous chunks didn't have the target id after it was found
finish=0 #did we finish searching?
arr_full= np.empty((0,1+4*maxp_r+2+1), float)
for gm_chunk in tp:
	#If tarid is not found in 
	if finish:	#complete if once found and later not found in 10 chunks
		print('finishing')
		#the waypoint and next point
		waypt=np.zeros((arr_full.shape[0],2),dtype=float)	#to store input or way point
		nextpt=np.zeros((arr_full.shape[0],2),dtype=float)	#to store output or next point
		for t_index in range(0,arr_full.shape[0],m+1):	#for all timestamps
			#way point
			for j in range(arr_full.shape[0]-1,t_index,-1): #reverse loop from end to now (excluding now=t_index's time)
				for k in range(m+1):	#for all radii
					vec=arr_full[j,[1+4*maxp_r,2+4*maxp_r]]-arr_full[t_index,[1+4*maxp_r,2+4*maxp_r]]
					dist=np.linalg.norm(vec)
					if dist>=rmin+k*delta:
						phi=np.arctan2(vec[1],vec[0])-arr_full[t_index,3+4*maxp_r]
						phi=norm_ang(phi)
						waypt[t_index+k,:]=[dist,phi]
			#next point
			if t_index==arr_full.shape[0]-1:
				dist=0
				phi=0
			else:
				vec=arr_full[t_index+1,[1+4*maxp_r,2+4*maxp_r]]-arr_full[t_index,[1+4*maxp_r,2+4*maxp_r]]
				dist=np.linalg.norm(vec)
				phi=np.arctan2(vec[1],vec[0])-arr_full[t_index,3+4*maxp_r]
				phi=norm_ang(phi)
			nextpt[t_index,:]=[dist,phi]
		
		arr_full[:,[1+4*maxp_r,2+4*maxp_r]]=waypt	#copy waypt
		arr_full=np.delete(arr_full,3+4*maxp_r,1)	#remove the extra temporary column
		arr_full=np.concatenate((arr_full,nextpt),axis=1)	#add nect pt
		np.savetxt(date+str(-target_time)+str(-tarid)+".csv", arr_full, delimiter=",")

		print 'Done!'
		break

	#Initialization
	#Don't do anything except load during initialization
	if init==1:
		init=0
		data=gm_chunk.values
		tstart=data[0,0]	#time at the first reading. Will be used to remove offset
		data[:,0]-=tstart	#remove time offset
		continue

	#Not init
	last_data=data
	data=gm_chunk.values
	data[:,0]-=tstart	#remove time offset
	
	#Check if target id is in last_data. If yes, then we check in rows of 'last_data and data' for the timestamp
	flag=-1
	for ii in range(chunksize):
		if last_data[ii,0]>=target_time and found==0:
			tarid=last_data[ii,1]
		if last_data[ii,1]==tarid:
			if found==0:
				print('found') #print found only whe  found for teh first time
			found=1
			flag=ii
			finish=0
			count=0
			break


	if flag==-1:
		if found:
			count+=1
			if count>=10:
				finish=1
				final_config=np.asarray([])
		continue #Skip the chunk if target id not found

	timestamp=last_data[ii,0]	#get the timestamp of where target id is
	#Also skip if timestamp is already dealt with
	if np.sum(timestamp==arr_full[:,0])!=0:
		continue

	
	arrt=np.concatenate((last_data,data),axis=0)	#combine 2 chunks of data
	arrt=arrt[np.where(arrt[:,0]==timestamp)]		#keep only the right timestamp's data

	##--Data is extracted, now compute the required quantities--#

	j0=np.where(arrt[:,1]==tarid)[0]	#index of target id

	arr=np.zeros((m+1,1+4*maxp+2+1), dtype=float) 	#4 rows for each surroundign person. 1 row extra for time stamp, 2 rows extra for goal. Space for goal storage is also temporarily used to store target id person's config in each timestamp
	arr[:,0]=timestamp
	k=0
	for j in range(arrt.shape[0]):
		if j!=j0:
			vec=arrt[j,[2,3]]-arrt[j0,[2,3]]		#difference in positions
			arr[m,k+1]=np.linalg.norm(vec)			#distance
			phi=np.arctan2(vec[1],vec[0])-arrt[j0,7]
			phi=norm_ang(phi)						#angle
			arr[m,k+2]=phi
			Vx=arrt[j,5]*np.cos(arrt[j,6])-arrt[j0,5]*np.cos(arrt[j0,6])	#Vx
			Vy=arrt[j,5]*np.sin(arrt[j,6])-arrt[j0,5]*np.sin(arrt[j0,6])	#Vy
			arr[m,k+3]=np.linalg.norm([Vx,Vy])	#V_mag
			arr[m,k+4]=np.arctan2(Vy,Vx)	#V_angle
			k+=4
	
	#arrange in increasing order of distance
	#selection sort
	for j in range(arrt.shape[0]-2): #in range of(number of surrounding people)-1=(arrt.shape[0]-1)-1=arrt.shape[0]-2. minus 1 because one person is target person, minus 1 because last oen is automatically sorted
		smallest=arr[m,1+j*4]
		smi=j
		for k in range(j+1,arrt.shape[0]-1):
			if arr[m,1+k*4]<smallest:
				smallest=arr[m,1+k*4]
				smi=k
		#swap if needed
		if smi!=j:
			temp=arr[m,[4*j+1,4*j+2,4*j+3,4*j+4]]
			arr[m,[4*j+1,4*j+2,4*j+3,4*j+4]]=arr[m,[4*smi+1,4*smi+2,4*smi+3,4*smi+4]]
			arr[m,[4*smi+1,4*smi+2,4*smi+3,4*smi+4]]=temp	
	
	#remove people outside rmax range
	for k in range(maxp_r):
		if arr[m,4*k+1]>rmax:
			arr[m,[4*k+1,4*k+2,4*k+3,4*k+4]]=0
			#print k
			#pass

	#remove extra columns
	arr=np.delete(arr,range((maxp_r)*4+1,(maxp)*4+1),1)	#remove the extra temporary column
	
	#fill up rows of arr except for for rmax which is already filled
	for j in range(0,m):	#for each radii except rmax
		for k in range(maxp_r):	#for each possibility within maxp no. of people
			if arr[m,4*k+1]<=rmin+delta*j:	
				arr[j,[4*k+1,4*k+2,4*k+3,4*k+4]]=arr[m,[4*k+1,4*k+2,4*k+3,4*k+4]]

	#Store target id person's position configuration
	arr[:,[1+4*maxp_r,2+4*maxp_r]]=arrt[j0,[2,3]]
	arr[:,3+4*maxp_r]=arrt[j0,7]	#target person's facing angle

	arr_full=np.concatenate((arr_full,arr),axis=0)
	i+=1