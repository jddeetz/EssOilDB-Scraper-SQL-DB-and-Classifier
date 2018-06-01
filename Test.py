from Grabber import GrabPage

url='http://www.nipgr.res.in/cgi-bin/disc/essoildb/details_2.cgi?pcode=JEACoitu.in2014Aer&cname=trans–beta-caryophyllene&cper=0.53&cexp=Thin%20Layered%20Chromatography%20(Hexane%20Extracts)'

Attributes=GrabPage(url)

print(Attributes)

