__author__ = 'SmartWombat'

bad_words = ['NIL']

with open('/home/roz016/Dropbox/Data for Tree/METAR source/ZBAA.txt') as oldfile, open('/home/roz016/Dropbox/Data for Tree/METAR source/ZBAA_nil.txt', 'w') as newfile:
    for line in oldfile:
        if not any(bad_word in line for bad_word in bad_words):
            newfile.write(line)