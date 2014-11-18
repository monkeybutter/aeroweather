__author__ = 'SmartWombat'

bad_words = ['Station:', 'You']

with open('/Users/SmartWombat/Desktop/LFPG.txt') as oldfile, open('/Users/SmartWombat/Desktop/metar_temp2.txt', 'w') as newfile:
    for line in oldfile:
        if not any(bad_word in line for bad_word in bad_words):
            newfile.write(line)