from Grabber import GrabPage
import re
import sqlite3
import time

conn = sqlite3.connect('essoil.sqlite')#connect to db or create
cur = conn.cursor()#database handle

#Set up tables from outermost to innermost
cur.executescript('''
CREATE TABLE IF NOT EXISTS ChemicalClass (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    class   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Chemical (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE,
    iupac  TEXT,
    formula  TEXT,
    cas    TEXT,
    url   TEXT,
    activity  TEXT,
    chemicalclass_id INTEGER   
);

CREATE TABLE IF NOT EXISTS PlantFamily (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    family   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Plant (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE,
    plantfamily_id INTEGER,
    url TEXT
);

CREATE TABLE IF NOT EXISTS PlantPart (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    part   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS PlantGroup (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    plantgroup  TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Article (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title   TEXT UNIQUE,
    year   TEXT,
    authors   TEXT,
    journal   TEXT,
    volume   TEXT
);

CREATE TABLE IF NOT EXISTS Location (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    location   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS ExpMethod (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    method   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS ExpCondition (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    condition   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Record (
    plant_id INTEGER,
    plantgroup_id INTEGER,
    plantpart_id INTEGER,
    expcondition_id INTEGER,
    location_id INTEGER,
    chemical_id INTEGER,
    percentage  FLOAT,
    expmethod_id INTEGER,
    http_link  TEXT UNIQUE,
    article_id  INTEGER,
    PRIMARY KEY (plant_id, chemical_id, article_id, expmethod_id, location_id, expcondition_id, plantpart_id, plantgroup_id));
''')

# Check to see if we are already in progress...
cur.execute('SELECT http_link FROM Record')
links_visited = cur.fetchall()

filename='Weeds.html'
fhandle=open(filename,'r')

html = fhandle.read()#read data from page
html_links=re.findall("<a href=\'(.*?)\'",html)

#Make a short list of "details" links
target_links=[]
for link in html_links:
    if 'details' in link:
        target_links.append(link)

#Visit and touch each link with below format
#http://www.nipgr.res.in/cgi-bin/disc/essoildb/details_2.cgi?pcode=JEOcrsaanco2004See&cname=1,8-cineole&cper=21.70&cexp=Normal
count=0
for link in target_links:
    if count<len(links_visited)-1:#Skip links already scanned 
        count=count+1
        print('Skipping link number',count,'. Already in database.')
        continue
    
    target_link='http://www.nipgr.res.in/cgi-bin/disc/essoildb/'+link
    target_link=target_link.replace(' ','%20')

    #Use function to grab data from page
    
    #url = safe_url_string(u'http://example.org/Ñöñ-ÅŞÇİİ/', encoding="utf-8")
    Attributes=GrabPage(target_link)
    
    #Write Attributes to the database
    cur.execute('''INSERT OR IGNORE INTO ChemicalClass (class)
    VALUES ( ? )''', ( Attributes['Chemica Classification'], ) )#If it is already there, do not insert it
    cur.execute('SELECT id FROM ChemicalClass WHERE class = ? ', (Attributes['Chemica Classification'], ))
    chemicalclass_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Chemical (name,iupac,formula,cas,url,
    activity,chemicalclass_id) VALUES ( ? , ? , ? , ? , ? , ? , ?)
    ''', (Attributes['Compound name'],Attributes['IUPAC'],Attributes['Formula'],Attributes['CAS'],Attributes['Compound link'],Attributes['Activity'],chemicalclass_id) )
    cur.execute('SELECT id FROM Chemical WHERE name = ? ', (Attributes['Compound name'], ))
    chemical_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO PlantFamily (family)
    VALUES ( ? )''', ( Attributes['Family'], ) )#If it is already there, do not insert it
    cur.execute('SELECT id FROM PlantFamily WHERE family = ? ', (Attributes['Family'], ))
    plantfamily_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Plant (name,plantfamily_id,url) VALUES ( ? , ? , ?)
    ''', (Attributes['Plant name'],plantfamily_id,Attributes['Plant link']) )
    cur.execute('SELECT id FROM Plant WHERE name = ? ', (Attributes['Plant name'], ))
    plant_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Article (title,year,authors,journal,volume)
    VALUES (?,?,?,?,?)''', (Attributes['Article Title'],Attributes['Year'],Attributes['Author'],Attributes['Journal'],Attributes['Volume']) )#If it is already there, do not insert it
    cur.execute('SELECT id FROM Article WHERE title = ? ', (Attributes['Article Title'], ))
    article_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Location (location)
    VALUES ( ? )''', ( Attributes['Location'], ) )
    cur.execute('SELECT id FROM Location WHERE location = ? ', (Attributes['Location'], ))
    location_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO PlantGroup (plantgroup)
    VALUES ( ? )''', ( Attributes['Group'], ) )
    cur.execute('SELECT id FROM PlantGroup WHERE plantgroup = ? ', (Attributes['Group'], ))
    plantgroup_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO ExpCondition (condition)
    VALUES ( ? )''', ( Attributes['Exp. Condition'], ) )
    cur.execute('SELECT id FROM ExpCondition WHERE condition = ? ', (Attributes['Exp. Condition'], ))
    expcondition_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO ExpMethod (method)
    VALUES ( ? )''', ( Attributes['Identification method'], ) )
    cur.execute('SELECT id FROM ExpMethod WHERE method = ? ', (Attributes['Identification method'], ))
    expmethod_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO PlantPart (part)
    VALUES ( ? )''', ( Attributes['Plant part'], ) )
    cur.execute('SELECT id FROM PlantPart WHERE part = ? ', (Attributes['Plant part'], ))
    plantpart_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Record
        (plant_id, plantgroup_id, plantpart_id, expcondition_id,location_id, chemical_id,percentage,expmethod_id,http_link,article_id) VALUES (?,?, ?,?,?, ?,?,?,?,? )''',
        ( plant_id, plantgroup_id, plantpart_id, expcondition_id, location_id, chemical_id,Attributes['Percentage'],expmethod_id,target_link,article_id ) )

    time.sleep(3)#Sleep to not overload server with requests
    
    count=count+1
    print('Visited',count,'links so far.')
    #if count>10: break
    if count%5==0: conn.commit() 

conn.commit()


