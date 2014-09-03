__author__ = 'SmartWombat'

"""
from parsers import tafor
tafor_code = "TAF YBBN 232338Z 2400/2506 09010KT 9999 -SHRA SCT018 BKN030 PROB30 TEMPO 2401/2409 04012KT 9999 -SHRA SCT020 SCT035 "
print(tafor_code)
frcst = tafor.Tafor(tafor_code)
print(frcst.tafor)
"""


from parsers import metar
metar_code = 'METAR YSSY 011930Z 20015KT 9000 FEW009 OVC016 21/18 Q1012 FM1930 18020KT 9999'
print(metar_code)
rep = metar.Metar(metar_code)
print(rep.metar)