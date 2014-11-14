__author__ = 'SmartWombat'

from pymongo import MongoClient
from parsers import metar
from datetime import datetime
from math import pow

m = 7.591386
Tn = 240.7263

#connection = MongoClient("ds053698.mongolab.com", 53698)
#db = connection["metar"]
# MongoLab has user authentication
#db.authenticate("metar", "metar")

#metar_coll = db['metar']

with open('./metar_temp3.txt', 'r') as f:
    for line in f:
        obs_date = datetime.strptime(line[:8], '%y-%m-%d')
        obs = metar.Metar("METAR" + line[8:])

        if obs.metar.has_key("datetime") and obs.metar.has_key("dewpoint"):
            obs_date = obs_date.replace(hour=obs.metar["datetime"].hour, minute=obs.metar["datetime"].minute)

            obj = {"airport": obs.metar["code"], "timestamp": obs_date}

            if obs.metar["temperature"] is not None and obs.metar["temperature"] != "//":
                obj["temperature"] = int(obs.metar["temperature"])
            else:
                obj["temperature"] = None

            if obs.metar["dewpoint"] is not None and obs.metar["temperature"] is not None and obs.metar["dewpoint"] != "//" and obs.metar["temperature"] != "//":
                a = int(obs.metar["dewpoint"]) / (int(obs.metar["dewpoint"]) + Tn)
                b = int(obs.metar["temperature"]) / (int(obs.metar["temperature"]) + Tn)
                obj["rel_humidity"] = round(100 * pow(10, m * (a - b)), 2)
            else:
                obj["rel_humidity"] = None

            if obs.metar["pressure"] is not None and obs.metar["pressure"] != "////":
                obj["pressure"] = int(obs.metar["pressure"])
            else:
                obj["pressure"] = None

            if obs.metar["wind"] is not None:

                obj["wind_dir"] = obs.metar["wind"]["dir"]

                if obs.metar["wind"]["speed"] is not None and obs.metar["wind"]["speed"] != "//":
                    obj["wind_spd"] = int(obs.metar["wind"]["speed"])

                    if obs.metar["wind"]["units"] == 'KT':
                        obj["wind_spd"] = round(obj["wind_spd"] * 0.51444444444, 2)
                    elif obs.metar["wind"]["units"] == 'MPS':
                        pass
                    else:
                        print(obs.metar["wind"]["units"])
                        obj["wind_spd"] = None
                else:
                    obj["wind_spd"] = None

            if obj["pressure"] is None:
                print line
                #break
            #metar_coll.insert(obj)
            print obj