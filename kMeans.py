import numpy as np
import pickle
import datetime
import matplotlib.pyplot as plt

#Load the data from before
data_store = pickle.load(open("data.pkl",'rb'))  
PlantNames=data_store[0]
ConcentrationsNorm=data_store[1][:,0:2]

#Initialize numpy random seed
np.random.seed(0) 

num_iter=10

#Initialize random centroids
def centroid_init(num_centr):
    centr_pos=np.random.rand(num_centr,2)
    return centr_pos

#Assign each point to a centroid
def centroid_assign(ConcentrationsNorm,centr_pos):
    ind=0
    centroid_assignments=np.zeros([len(ConcentrationsNorm)])
    for row in ConcentrationsNorm:
        norms=np.sum((centr_pos-row)**2,axis=1)
        index_min = np.argmin(norms)
        centroid_assignments[ind]=index_min
        ind+=1
    return centroid_assignments

#Move centroids
def move_centroids(ConcentrationsNorm,centr_pos,centroid_assignments):
    #Find the average of the points
    sum_centr_pos=np.zeros([num_centr,2])
    for i in range(len(centroid_assignments)):
        sum_centr_pos[centroid_assignments[i]]+=ConcentrationsNorm[i,:]
    #Normalize by the number of points
    for j in range(num_centr):
        centr_pos[j,0:2]=sum_centr_pos[j,0:2]/list(centroid_assignments).count(j)
    #print(sum_centr_pos)
    #print(centr_pos)
    return centr_pos

#Implement k-Means clustering Algorithm
for num_centr in [3]:
    print('Initializing',num_centr,'centroid positions')
    centr_pos=centroid_init(num_centr)
    print(centr_pos)

    print('Assigning each point to a centroid')
    centroid_assignments=centroid_assign(ConcentrationsNorm,centr_pos)
    print(centroid_assignments)

    #If one of the centroids has no points, initiate a new random seed and initialize and assign again
    while len(set(centroid_assignments)) < 3:
        print('A cluster had no points, starting again...')
        np.random.seed(int(str(datetime.datetime.now().time())[-2:]))
        print('Initializing',num_centr,'centroid positions')
        centr_pos=centroid_init(num_centr)
        print(centr_pos) 
        print('Assigning each point to a centroid')
        centroid_assignments=centroid_assign(ConcentrationsNorm,centr_pos)
        print(centroid_assignments)
    
    for n in range(num_iter):
        print('Beginning iteration number',n)
        #Move the positions of the centroids to the average positions of the points assigned to them.
        print('Moving each centroid')
        centr_pos=move_centroids(ConcentrationsNorm,centr_pos,centroid_assignments)
        print(centr_pos)
        print('Assigning each point to a centroid')
        centroid_assignments=centroid_assign(ConcentrationsNorm,centr_pos)
        print(centroid_assignments)

plt.scatter(ConcentrationsNorm[:,0],ConcentrationsNorm[:,1],color='r')
plt.scatter(centr_pos[:,0],centr_pos[:,1],color='b')
plt.xlabel('Monoterpene Concentration')
plt.ylabel('Sesquiterpene/Diterpene Concentration')

for centr in range(num_centr):
    print('The plants belonging to type',centr,'are:')
    for j in range(len(centroid_assignments)):
        if centroid_assignments[j]==centr:
            print(PlantNames[j])
    print('\n')




