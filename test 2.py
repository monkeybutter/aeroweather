__author__ = 'SmartWombat'

from parsers import tafor
from parsers import metar
from datetime import datetime
from math import pow
import pymongo

m = 7.591386
Tn = 240.7263

import pymongo
from pymongo import MongoClient

connection = MongoClient("ds053698.mongolab.com", 53698)
#db = connection["metar"]
# MongoLab has user authentication
#db.authenticate("metar", "metar")

"""

db = client.get_default_database()

metar = db['metar']


with open('/Users/SmartWombat/Dropbox/Data for Tree/METAR source/ZBAA.txt', 'r') as f:
        for line in f:
            obs_date = datetime.strptime(line[:8], '%y-%m-%d')
            obs = metar.Metar("METAR" + line[8:])

            if obs.metar.has_key("datetime") and obs.metar.has_key("dewpoint"):
                obs_date = obs_date.replace(hour=obs.metar["datetime"].hour, minute=obs.metar["datetime"].minute)
                #print(obs.metar)

                obj = {}

                obj["airport"] = obs.metar["code"]

                obj["datetime"] = obs_date

                if obs.metar["temperature"] is not None:
                    obj["temperature"] = int(obs.metar["temperature"])
                else:
                    obj["temperature"] = None

                if obs.metar["dewpoint"] is not None and obs.metar["temperature"] is not None:
                    a = int(obs.metar["dewpoint"]) / (int(obs.metar["dewpoint"]) + Tn)
                    b = int(obs.metar["temperature"]) / (int(obs.metar["temperature"]) + Tn)
                    obj["rel_humidity"] = 100 * pow(10, m * (a - b))
                else:
                    obj["rel_humidity"] = None

                if obs.metar["pressure"] is not None:
                    obj["pressure"] = int(obs.metar["pressure"])
                else:
                    obj["pressure"] = None

                if obs.metar["wind"] is not None:

                    obj["wind_dir"] = obs.metar["wind"]["dir"]

                    if obs.metar["wind"]["speed"] is not None:
                        obj["wind_spd"] = int(obs.metar["wind"]["speed"])

                        if obs.metar["wind"]["units"] == 'KT':
                            obj["wind_spd"] = obj["wind_spd"] * 0.51444444444
                        elif obs.metar["wind"]["units"] == 'MPS':
                            pass
                        else:
                            print("ERROR")
                            break
                    else:
                        obj["wind_spd"] = None


                metar.insert(obj)
"""