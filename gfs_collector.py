"""
This connects to the envirohack database which is hosted on mongolab, and uploads new data from 
http://opendap.bom.gov.au (overwriting old data). It is meant to be connected to a cron job which will 
update the database once per day.
"""

import urllib2
import sys
import re
from datetime import timedelta, datetime
from collections import OrderedDict
import numpy as np
from pymongo import MongoClient
from math import sqrt, pow, atan2, pi

def getDate():
    base_url = 'http://opendap.bom.gov.au:8080/thredds/catalog/nmoc/access-sy-fc/ops/surface/latest/'
    usock = urllib2.urlopen(base_url)
    data = usock.read()
    usock.close()

    for line in data.split('\n'):
        match = re.search(r"ACCESS-SY_(\d+)_", line)
        if (match):
            return match.group(1)

def get_gfs_indices(lat, lon):
    lats = np.arange(90.0, -90.5, -.5)
    lons = np.arange(0.0, 360.0, .5)

    dist_lat = sys.float_info.max
    best_lat = -1
    for ind_lat, val_lat in np.ndenumerate(lats):
        if abs(val_lat - lat) < dist_lat:
            dist_lat = abs(val_lat - lat)
            best_lat = ind_lat

    dist_lon = sys.float_info.max
    best_lon = -1
    for ind_lon, val_lon in np.ndenumerate(lons):
        if abs(val_lon - lon) < dist_lon:
            dist_lon = abs(val_lon - lon)
            best_lon = ind_lon

    return best_lat[0], best_lon[0]


def parse_value(line):
    return float(line.split(',')[-1])


def get_data(lines):

    data = {}
    for i, line in enumerate(lines):

        if line == 'U-component_of_wind_height_above_ground.U-component_of_wind_height_above_ground[1][1][1][1]':
            data["uwind"] = parse_value(lines[i+1])

        elif line == 'V-component_of_wind_height_above_ground.V-component_of_wind_height_above_ground[1][1][1][1]':
            data["vwind"] = parse_value(lines[i+1])

        elif line == 'Relative_humidity_height_above_ground.Relative_humidity_height_above_ground[1][1][1][1]':
            data["rh"] = parse_value(lines[i+1])

        elif line == 'Pressure_surface.Pressure_surface[1][1][1]':
            data["press"] = parse_value(lines[i+1])/100

        elif line == 'Temperature_height_above_ground.Temperature_height_above_ground[1][1][1][1]':
            data["temp"] = parse_value(lines[i+1])

    return data

"""
ZBAA ()
YSSY (-33.9461, 151.1772)
EGLL (51.4775, 360.0-0.4614)
KATL (33.6367, 360.0-84.4281)

"""

airport = {}
airport['code'] = 'LEBL'
airport['lat'] = 41.296944
airport['lon'] = 2.078333

airport = {}
airport['code'] = 'LFPG'
airport['lat'] = 49.009722
airport['lon'] = 2.547778

airport = {}
airport['code'] = 'LIMC'
airport['lat'] = 45.63
airport['lon'] = 8.723056

airport = {}
airport['code'] = 'EDDT'
airport['lat'] = 52.559722
airport['lon'] = 13.287778

if __name__ == "__main__":

    gfs_indices = get_gfs_indices(airport['lat'], airport['lon'])

    start_date = datetime(2013, 11, 15)

    connection = MongoClient("ds053698.mongolab.com", 53698)
    db = connection["metar"]
    # MongoLab has user authentication
    db.authenticate("metar", "metar")

    gfs_coll = db['gfs']

    runs = OrderedDict([(0, "_0000_"), (6, "_0600_"), (12, "_1200_"), (18, "_1800_")])
    leads = OrderedDict([(0, "000"), (3, "003")])

    day_count = 40

    for day_date in (start_date + timedelta(n) for n in range(day_count)):
        for int_run, str_run in runs.iteritems():
            for int_lead, str_lead in leads.iteritems():
                url = 'http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/' + day_date.strftime("%Y%m") + \
                      '/' + day_date.strftime("%Y%m%d") + '/gfsanl_4_' + day_date.strftime("%Y%m%d") + \
                      str_run + str_lead + '.grb2.ascii?U-component_of_wind_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'V-component_of_wind_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'Pressure_surface[0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'Relative_humidity_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'Temperature_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + ']'


                try:
                    data = urllib2.urlopen(url).read()
                    run_date = day_date + timedelta(hours=int_run)
                    value_date = run_date + timedelta(hours=int_lead)

                    raw = get_data(data.split('\n'))


                    obj = {}

                    obj["airport"] = airport['code']
                    obj["timestamp"] = value_date
                    obj["temperature"] = round(raw['temp'] - 273.15, 2)
                    obj["rel_humidity"] = raw['rh']
                    obj["pressure"] = round(raw['press'], 2)
                    obj["wind_spd"] = round(sqrt(pow(raw['uwind'], 2) + pow(raw['vwind'], 2)), 2)
                    obj["wind_dir"] = int(-1 * (180.0 * atan2(raw['vwind'], raw['uwind']) / pi + 90) % 360)
                    gfs_coll.insert(obj)
                    print value_date
                    print obj


                except urllib2.HTTPError, e:
                    print(e.code)
                    continue
                except urllib2.URLError, e:
                    print(e.args)
                    continue