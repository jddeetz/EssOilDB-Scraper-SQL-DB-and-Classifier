import sqlite3
import numpy as np
import pickle

# Connect to the database
conn = sqlite3.connect('essoil.sqlite')#connect to db or create
cur = conn.cursor()#database handle

# Get the names of the Plants and Chemical Classes
cur.execute('SELECT name FROM Plant')
PlantNames = cur.fetchall()

cur.execute('SELECT class FROM ChemicalClass')
ChemicalClasses = cur.fetchall()

#Convert list of tuples into list of lists
tmp=list()
for item in PlantNames:
    tmp.append(item[0])
PlantNames=tmp

tmp=list()
for item in ChemicalClasses:
    tmp.append(item[0])
ChemicalClasses=tmp

#For each plant, retrieve concentrations of monoterpenes (index 0), sesquiterpenes (index 1), diterpenes (index 2), and others (index 3)
#If a plant does not have any terpenes, do not add it to the data.
 
#Create a numpy array to store Concentrations, which will look like this Concentrations[plantnum][chemicalclass]=0.35
Concentrations=np.zeros([len(PlantNames),3])
ConcentrationsNorm=np.zeros([len(PlantNames),3])
plantnum=0

#Join Plant, Chemical, and ChemicalClass tables and retrieve concentrations
for plant_name in PlantNames:
    cur.execute('''SELECT ChemicalClass.class,Chemical.name,Record.percentage FROM Record
    JOIN Plant JOIN Chemical JOIN ChemicalClass ON Plant.id = Record.plant_id
    AND Chemical.id = Record.chemical_id AND Chemical.chemicalclass_id = ChemicalClass.id
    WHERE Plant.name = ?''',(plant_name,))
    results=cur.fetchall()
    for chemical in results:
        #If chemical concentration is 'trace' or 'tr' or some other string, move past it
        if isinstance(chemical[2],str) is True: continue 

        #If chemical class is a monoterpene, sesquiterpene, diterpene, or other, add it to the Concentrations variable
        if 'monoterp' in chemical[0]:
            Concentrations[plantnum][0]=Concentrations[plantnum][0]+chemical[2]
        elif ('sesquiterp' in chemical[0]) or ('diterp' in chemical[0]):
            Concentrations[plantnum][1]=Concentrations[plantnum][1]+chemical[2]
        else:
            Concentrations[plantnum][2]=Concentrations[plantnum][2]+chemical[2]

    #Obtain number of records corresponding to a single plant
    cur.execute('''SELECT Record.plantgroup_id,Record.article_id,Record.expcondition_id,Record.location_id,Record.expmethod_id 
    FROM Record JOIN Plant ON Plant.id = Record.plant_id WHERE Plant.name = ?''',(plant_name,))
    results=cur.fetchall()
    #Normalize each set of concentrations by the number of experiments
    ConcentrationsNorm[plantnum]=Concentrations[plantnum]/len(set(results))
    ConcentrationsNorm[plantnum]=ConcentrationsNorm[plantnum]/sum(ConcentrationsNorm[plantnum])
    plantnum+=1

#Two plants show up twice, but under different names: 'Ageratum Conyzoides', 'Ageratum conyzoides'
#Also 'NA' shows up as a plant name, but it is clearly not a plant. Some species have zero reported monoterpene/sesquiterpene concentrations
#Correct these mistakes
ConcentrationsNorm=np.delete(ConcentrationsNorm,22, 0)
PlantNames.remove('NA')
ConcentrationsNorm[0,:]=(ConcentrationsNorm[0,:]+ConcentrationsNorm[1,:])/2
ConcentrationsNorm=np.delete(ConcentrationsNorm,1, 0)
PlantNames.remove('Ageratum Conyzoides')
ConcentrationsNorm=np.delete(ConcentrationsNorm,4, 0)
PlantNames.remove('Cedrela odorata')
ConcentrationsNorm=np.delete(ConcentrationsNorm,26, 0)
PlantNames.remove('Tagetes minuta')

#Finally, we have a list of plant names and an array of monoterpene, sesquiterpene/diterpene, and other percentages
print(PlantNames)
print(ConcentrationsNorm)

#Store data in pkl file
data_store=[PlantNames,ConcentrationsNorm]
pickle.dump(data_store, open("data.pkl",'wb') )

