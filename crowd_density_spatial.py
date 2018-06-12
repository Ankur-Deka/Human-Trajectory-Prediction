#function to compute the crowd density at different locations over time for one file
import pandas as pd
import numpy as np	#Because I a like it
import matplotlib.pyplot as plt

chunksize=100000
date='20121125'
tp = pd.read_csv('/usr/atc-dataset/atc-'+date+'.csv', header=None, iterator=True, chunksize=chunksize, low_memory=False)
xmin,xmax,ymin,ymax=-60,60,-60,60
density_map=np.zeros((xmax-xmin+1,ymax-ymin+1),dtype=float)
i=0

for gm_chunk in tp:
	print('Chunk: ', i)
	#Load the chunk (only positions)
	data=gm_chunk.values[:,range(2,4)]
	for ii in range(chunksize):
		[x,y]=data[ii]
		density_map[int(x/1000)+xmin,int(y/1000)+ymin]+=1

	i+=1
	if i>100		:
		break
	
#temp=density_map[:,0]
#density_map[:,0]=density_map[:,1]
#density_map[:,1]=temp

plt.imshow(density_map.T, cmap='hot', interpolation='none', extent=[xmin,xmax,ymax,ymin])
plt.gca().invert_yaxis()
plt.colorbar()
plt.show()
