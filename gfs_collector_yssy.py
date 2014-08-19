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


def parseLines(lines, index, precip, temperature):
    trackingPrcp = False
    trackingTemp = False
    for line in lines:
        if line.strip() == 'accum_prcp.accum_prcp[1][25][25]':
            trackingPrcp = True
            continue
        if trackingPrcp == True:
            if line.strip() == 'accum_prcp.time[1]':
                trackingPrcp = False
                continue
            if line.strip() == '':
                continue
            row = line.split(',')
            key = row.pop(0);
            rowIndex = re.search('\[\d+\]\[(\d+)\]', key).group(1)
            row = [float(value.strip()) for value in row]
            precip["%s_%s" % (i, rowIndex)] = row
        if line.strip() == 'sfc_temp.sfc_temp[1][25][25]':
            trackingTemp = True
            continue
        if trackingTemp == True:
            if line.strip() == 'sfc_temp.time[1]':
                trackingTemp = False
                continue
            if line.strip() == '':
                continue
            row = line.split(',')
            key = row.pop(0);
            rowIndex = re.search('\[\d+\]\[(\d+)\]', key).group(1)
            row = [float(value.strip()) - 273.15 for value in row]
            temperature["%s_%s" % (i, rowIndex)] = row


def readfile(usock):
    contents = usock.read()
    lines = contents.split("\n")
    print lines
    #parseLines(lines, i, precipitationDict, temperatureDict)


def writeToDatabase(lonList, latList, precipitationDict, temperatureDict, datetime):
    for lt, lat in enumerate(latList):
        for ln, lon in enumerate(lonList):
            precipThroughTimeList = []
            tempThroughTimeList = []
            for i in range(37):
                lonRow = precipitationDict["%s_%s" % (i, lt)]
                precipThroughTimeList.append(lonRow[ln])
                lonRow = temperatureDict["%s_%s" % (i, lt)]
                tempThroughTimeList.append(lonRow[ln])
            recordDict = {
                "_id": "%s_%s" % (lon, lat),
                "precipitation": precipThroughTimeList,
                "temperature": tempThroughTimeList,
                "location": {
                    "type": "Point",
                    "coordinates": [
                        lon,
                        lat
                    ]
                },
                "datetime": datetime
            }
            db.weather_at_point.update({"_id": "%s_%s" % (lon, lat)}, recordDict, True)


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


if __name__ == "__main__":

    gfs_indices = get_gfs_indices(-33.9461, 151.1772)
    print gfs_indices

    start_date = datetime(2013, 12, 15)
    runs = OrderedDict([(0, "_0000_"), (6, "_0600_"), (12, "_1200_"), (18, "_1800_")])
    leads = OrderedDict([(0, "000"), (3, "003")])

    day_count = 17

    f_out=open('./data_yssy2.csv', 'w')
    f_out.write('date, time, uwind, vwind, temp, rh\n')

    for day_date in (start_date + timedelta(n) for n in range(day_count)):
        for int_run, str_run in runs.iteritems():
            for int_lead, str_lead in leads.iteritems():
                url = 'http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/' + day_date.strftime("%Y%m") + \
                      '/' + day_date.strftime("%Y%m%d") + '/gfsanl_4_' + day_date.strftime("%Y%m%d") + \
                      str_run + str_lead + '.grb2.ascii?U-component_of_wind_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'V-component_of_wind_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'Relative_humidity_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + '],' + \
                      'Temperature_height_above_ground[0][0][' + str(gfs_indices[0]) + '][' + str(gfs_indices[1]) + ']'

                try:
                    data = urllib2.urlopen(url).read()
                    run_date = day_date + timedelta(hours=int_run)
                    value_date = run_date + timedelta(hours=int_lead)

                    lista = data.split('\n')

                    print(value_date.strftime("%Y%m%d  %H:%M"))
                    uwind = lista[40].split(',')[1].strip()
                    rh = lista[56].split(',')[1].strip()
                    temp = lista[72].split(',')[1].strip()
                    vwind = lista[88].split(',')[1].strip()

                    f_out.write('{}, {}, {}, {}, {}, {}\n'.format(value_date.strftime("%Y%m%d"), value_date.strftime("%H:%M"), uwind, vwind, temp, rh))

                except urllib2.HTTPError, e:
                    print(e.code)
                    continue
                except urllib2.URLError, e:
                    print(e.args)
                    continue


    f_out.close()
"""
	connection = MongoClient("ds053139.mongolab.com", 53139)
db = connection["gfs"]
# MongoLab has user authentication
db.authenticate("sensordb", "Csiro2012")
    date = getDate()

    for i in range(37):
        url = 'http://opendap.bom.gov.au:8080/thredds/dodsC/nmoc/access-sy-fc/ops/surface/' + date + '/ACCESS-SY_' + date + '_%03d_surface.nc.ascii?accum_prcp[0:1:0][141:1:165][45:1:69],sfc_temp[0:1:0][141:1:165][45:1:69]' % i
        usock = urllib2.urlopen(url)
        readfile(usock, lon, lat, i, precipitationDict, temperatureDict)
        usock.close()
    writeToDatabase(lon, lat, precipitationDict, temperatureDict, date)

http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/201310/20131027/gfsanl_4_20131027_0600_003.grb2.ascii?U-component_of_wind_height_above_ground[0:1:0][0:1:0][248:1:248][302:1:302],V-component_of_wind_height_above_ground[0:1:0][0:1:0][248:1:248][302:1:302],Total_cloud_cover_low_cloud[0:1:0][248:1:248][302:1:302],Total_cloud_cover_middle_cloud[0:1:0][248:1:248][302:1:302],Total_cloud_cover_high_cloud[0:1:0][248:1:248][302:1:302]
http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/201310/20131027/gfsanl_4_20131027_0600_003.grb2.ascii?U-component_of_wind_height_above_ground[1][1][248][302],V-component_of_wind_height_above_ground[1][1][248][302]
http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/201205/20120530/gfsanl_4_20120530_0600_003.grb2.ascii?U-component_of_wind_height_above_ground[1][1][248][302],V-component_of_wind_height_above_ground[1][1][248][302]
http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/201310/20131027/gfsanl_4_20131027_0600_003.grb2.ascii?U-component_of_wind_height_above_ground[0:1:0][0:1:0][248:1:248][302:1:302],V-component_of_wind_height_above_ground[0:1:0][0:1:0][248:1:248][302:1:302],Total_cloud_cover_low_cloud[0:1:0][248:1:248][302:1:302],Total_cloud_cover_middle_cloud[0:1:0][248:1:248][302:1:302],Total_cloud_cover_high_cloud[0:1:0][248:1:248][302:1:302]
http://nomads.ncdc.noaa.gov/thredds/dodsC/gfs-004-anl/201310/20131027/gfsanl_4_20131027_0600_003.grb2.ascii?U-component_of_wind_height_above_ground[0:1:0][0:1:0][248:1:248][302:1:302],V-component_of_wind_height_above_ground[0:1:0][0:1:0][248:1:248][302:1:302],Total_cloud_cover_low_cloud[0:1:0][248:1:248][302:1:302],Total_cloud_cover_middle_cloud[0:1:0][248:1:248][302:1:302],Total_cloud_cover_high_cloud[0:1:0][248:1:248][302:1:302]
	"""