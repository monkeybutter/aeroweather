__author__ = 'SmartWombat'

bad_words = ['NIL']

with open('/Users/SmartWombat/Dropbox/Data for Tree/YSSY.txt') as oldfile, open('/Users/SmartWombat/Dropbox/Data for Tree/YSSY_clean.txt', 'w') as newfile:
    for line in oldfile:
        if not any(bad_word in line for bad_word in bad_words):
            newfile.write(line)