"""
This connects to the envirohack database which is hosted on mongolab, and uploads new data from 
http://opendap.bom.gov.au (overwriting old data). It is meant to be connected to a cron job which will 
update the database once per day.
"""

from datetime import timedelta, datetime
from collections import OrderedDict
import numpy as np
from pymongo import MongoClient
import h5py

if __name__ == "__main__":

    """
    YSSY_loc = (-33.9461, 151.1772)

    connection = MongoClient("ds053698.mongolab.com", 53698)
    db = connection["metar"]
    # MongoLab has user authentication
    db.authenticate("metar", "metar")

    gfs_coll = db['era']
    """

    filename = "/home/roz016/Dropbox/Data for Tree/ERA Interim/YSSY2011.h5"

    with h5py.File(filename, 'r') as f:

        print(f)
        print(f.name)
        print(f.keys())
        df = f["v10"]
        print(df)