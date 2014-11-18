__author__ = 'SmartWombat'


from parsers import metar

obs = metar.Metar("METAR EDDT 140250Z 21003KT 0500 R26R/0750N R26L/0800N FG OVC001 00/00")

print obs.metar