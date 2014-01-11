#!/usr/bin/python
#
#  Nov 10, 2013 
#  Pablo Rozas-Larraondo
#

import re
from parsers import metar
from parsers import tafor

from pymongo import MongoClient
import urllib2
import BeautifulSoup

def url_metar(airport):
    return 'http://www.aviationweather.gov/adds/metars/?station_ids=' + \
    airport + '&std_trans=standard&chk_metars=on&hoursStr=most+recent+only&submitmet=Submit'

def url_tafor(airport):
    return 'http://www.aviationweather.gov/adds/tafs/?station_ids=' + \
    airport + '&std_trans=standard&submit_taf=Get+TAFs'

airports = ['YSSY', 'YSCB', 'YMML', 'YMHB', 'YPPH', 'YBBN', 'YPAD']

for airport in airports:
    usock = urllib2.urlopen(url_metar(airport))
    data_metar = usock.read()
    usock.close()
    
    soup = BeautifulSoup.BeautifulSoup(data_metar)
    metar_code = soup.font.string.replace('\n','')
    metar_code = re.sub(' +',' ',metar_code)
    
    usock = urllib2.urlopen(url_tafor(airport))
    data_tafor = usock.read()
    usock.close()
    
    soup = BeautifulSoup.BeautifulSoup(data_tafor)
    tafor_code = soup.font.string.replace('\n','')
    tafor_code = re.sub(' +',' ',tafor_code)
    
    
    obs = metar.Metar(metar_code)
    frcst = tafor.Tafor(tafor_code)
    
    connection = MongoClient("ds053698.mongolab.com", 53698)
    db = connection["metar"]
    # MongoLab has user authentication
    db.authenticate("metar", "metar")
    
    collection = db.metar
    if (collection.find({"code": airport}).sort([('_id', -1)]).limit(1)[0]['datetime'] != obs.metar['datetime']):
        collection.insert(obs.metar)
        print('{} metar written to DB'.format(airport))
      
    collection = db.tafor
    #if (collection.find({"code": airport}).sort([('_id', -1)]).limit(1)[0]['datetime'] != frcst.tafor['datetime']):
    collection.insert(frcst.tafor)
    print('{} tafor written to DB'.format(airport))
