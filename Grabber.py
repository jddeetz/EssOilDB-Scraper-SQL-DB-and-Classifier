#import urllib.request, urllib.parse, urllib.error, urllib
from bs4 import BeautifulSoup
import unidecode
import requests

def GrabPage(url):
    print('Getting data from',url)
    
    #Get html data from url
    response = requests.get(url)
    data=response.text
    #Remove some troublesome tags
    data=data.replace('<i>','').replace('</i>','')
    data=data.replace('<sub>','').replace('</sub>','')
    #Parse data with bs4
    soup = BeautifulSoup(data, "html.parser")

    Attributes=dict()

    #Find number of bold tags, # of attributes listed in record
    num_attr=len(soup('b'))

    #for each attribute
    for attr_id in range(num_attr):
        #finds the table
        tree=soup.find('table', align="center", cellpadding="2").contents[attr_id]
        #print(tree.prettify())

        #grab the attribute and its value
        attr=tree.contents[0].contents[0].string.lstrip()
        val=tree.contents[0].contents[1].string

        #If compund name or plant name, grab html links to external sites
        if attr=="Compound name" and len(tree('a'))>0:
            tag=tree('a')[0]
            href=tag.get('href', None)
            Attributes["Compound link"]=href
        elif attr=="Plant name":
            #print(tree.prettify())
            val=tree('a')[0].string #contents[0]
            Attributes["Plant name"]=val
            if len(tree('a'))>0:
                tag=tree('a')[0]
                href=tag.get('href', None)
                Attributes["Plant link"]=href
            
        #print(val)
        Attributes[attr]=val
        if Attributes[attr] is None:
            print('Failure to retrieve',attr,'!!!!!!')
            Attributes[attr]='NA'
    
    return Attributes
