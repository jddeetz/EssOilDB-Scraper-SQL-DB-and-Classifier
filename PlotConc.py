import numpy as np
import pickle
import matplotlib.pyplot as plt

#Load the data from before
data_store = pickle.load(open("data.pkl",'rb'))  
PlantNames=data_store[0]
ConcentrationsNorm=data_store[1]

#print(PlantNames)
print(ConcentrationsNorm)

plt.scatter(ConcentrationsNorm[:,0],ConcentrationsNorm[:,1],color='r')
plt.xlabel('Monoterpene Concentration')
plt.ylabel('Sesquiterpene/Diterpene Concentration')
