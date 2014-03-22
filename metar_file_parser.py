__author__ = 'SmartWombat'

from parsers import metar

airport = 'YSSY'

with open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean.txt'.format(airport), 'r') as f, open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean.csv'.format(airport), 'w') as csv:
    for line in f:
        csv_line = ''
        write = True
        metaro = metar.Metar(line)

        csv_line += metaro.metar['datetime'].strftime('%Y-%m-%d,%H:%M') + ','

        if metaro.metar['wind'] is not None:
            if metaro.metar['wind']['dir'] == 'VRB':
                write = False
            if metaro.metar['wind']['speed'] == '00':
                write = False
            csv_line += metaro.metar['wind']['dir'] + ',' + metaro.metar['wind']['speed'] + ','
        else:
            write = False
            csv.write(',,')

        if metaro.metar['temperature'] is not None:
            csv_line += metaro.metar['temperature'] + ',' +  metaro.metar['dewpoint'] + ','
        else:
            write = False
            csv.write(',,')

        if metaro.metar['pressure'] is not None:
            csv_line += metaro.metar['pressure']
        else:
            write = False

        if write:
            csv.write(csv_line + '\n')

lines_seen = set() # holds lines already seen
outfile = open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean_nodups.csv'.format(airport), 'w')
for line in open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean.csv'.format(airport), 'r'):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

def get_line(metar):

    return ""