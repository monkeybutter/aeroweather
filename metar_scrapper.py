#!/usr/bin/python
 
import urllib2
import re
import datetime

with open("petar_temp.txt", "w") as metar:
        
    startDate = datetime.date(2011, 6, 16)
    endDate = datetime.date(2012, 2, 1)
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
                print(line)
        startDate += delta
