#!/usr/bin/python
 
import urllib2
import re
import datetime

with open("metar_temp.txt", "w") as metar:
        
    startDate = datetime.date(2012, 1, 2)
    endDate = datetime.date(2012, 8, 1)
    delta = datetime.timedelta(days=1)

    while startDate <= endDate:
        print startDate.strftime("%y-%m-%d ")
        request = startDate.strftime("http://vortex.plymouth.edu/cgi-bin/gen_statlog-u.cgi?ident=LFPG&pl=none0&yy=" + "%y" + "&mm=" + "%m" + "&dd=" + "%d")
        response = urllib2.urlopen(request)

        semaphore = False

        for line in response.read().split('\n'):
            match = re.search('^\s+', line)
            if match and semaphore is True:
                metar.write(' ' + ' '.join(line.split()))

            else:
                match = re.search('^METAR LFPG', line)
                if match:
                    semaphore = True
                    metar.write('\n' + startDate.strftime("%y-%m-%d ") + ' '.join(line.split()))
                else:
                    semaphore = False

        startDate += delta
