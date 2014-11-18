__author__ = 'SmartWombat'


from parsers import metar

obs = metar.Metar("METAR EDDT 060550Z 26018KT 9999 RA FEW003 BKN008 OCV010 09/08 Q1014 R88/29//95 NOSIG")

print obs