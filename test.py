__author__ = 'SmartWombat'

from parsers import tafor
tafor_code = "TAF YBBN 232338Z 2400/2506 09010KT 9999 -SHRA SCT018 BKN030 PROB30 TEMPO 2401/2409 04012KT 9999 -SHRA SCT020 SCT035 "
print(tafor_code)
frcst = tafor.Tafor(tafor_code)
print(frcst.tafor)