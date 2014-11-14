#!/usr/bin/python
 
import urllib2
import re
import datetime

metar = open("metar_temp.txt", "w")
        
startDate = datetime.date(2011, 1, 1)
endDate = datetime.date(2011, 9, 1)
delta = datetime.timedelta(days=1)

delta = datetime.timedelta(days=1)
while startDate <= endDate:
    print startDate.strftime("%y-%m-%d ")
    request = startDate.strftime("http://vortex.plymouth.edu/cgi-bin/gen_statlog-u.cgi?ident=LEBL&pl=none0&yy=" + "%y" + "&mm=" + "%m" + "&dd=" + "%d")
    response = urllib2.urlopen(request)
    for line in response.read().split('\n'):
        match = re.search('^LEBL', line)
        if match:
            metar.write('\n' + startDate.strftime("%y-%m-%d ") + line)
        else:
            metar.write(line)
    startDate += delta
