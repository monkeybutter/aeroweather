__author__ = 'SmartWombat'

from parsers import metar

airports = ['EGLL','YSSY']

for airport in airports:

    bad_words = ['NIL']

    with open('/Users/SmartWombat/Dropbox/Data for Tree/{}.txt'.format(airport)) as oldfile, open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean.txt'.format(airport), 'w') as newfile:
        for line in oldfile:
            if not any(bad_word in line for bad_word in bad_words):
                newfile.write(line)

    with open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean.txt'.format(airport), 'r') as f, open('/Users/SmartWombat/Dropbox/Data for Tree/{}_clean.csv'.format(airport), 'w') as csv:
        for line in f:
            csv_line = ''
            write = True
            metaro = metar.Metar(line)
            #print metaro.metar['datetime'].strftime('%Y-%m-%d,%H:%M')
            csv_line += metaro.metar['datetime'].strftime('%Y-%m-%d,%H:%M') + ','

            if metaro.metar['wind'] is not None:
                if metaro.metar['wind']['dir'] == 'VRB':
                    write = False
                if metaro.metar['wind']['dir'] == '//':
                    write = False
                if metaro.metar['wind']['speed'] == '00':
                    write = False
                if metaro.metar['wind']['speed'] == '//':
                    write = False
                csv_line += metaro.metar['wind']['dir'] + ',' + metaro.metar['wind']['speed'] + ','
            else:
                write = False
                csv_line += ',,'

            if metaro.metar['temperature'] is not None:
                if metaro.metar['temperature'] == '//':
                    write = False
                if metaro.metar['dewpoint'] == '//':
                    write = False
                csv_line += metaro.metar['temperature'] + ',' +  metaro.metar['dewpoint'] + ','
            else:
                write = False
                csv_line += ',,'

            if metaro.metar['pressure'] is not None:
                if metaro.metar['pressure'] == '//':
                    write = False
                csv_line += metaro.metar['pressure']
            else:
                write = False
                csv_line += ''

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