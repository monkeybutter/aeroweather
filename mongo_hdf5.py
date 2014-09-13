import pandas as pd
from pymongo import MongoClient




def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    conn = MongoClient(host, port)
    db = conn[db]
    db.authenticate(username, password)


    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    print db[collection].distinct("airport")

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df

if __name__ == "__main__":
    store = pd.HDFStore('/Users/monkeybutter/Desktop/store.h5')
    df = read_mongo('metar', 'metar', {}, 'ds053698.mongolab.com', 53698, 'metar', 'metar')
    print("done metar")
    store["metar"] = df
    df = read_mongo('metar', 'gfs', {}, 'ds053698.mongolab.com', 53698, 'metar', 'metar')
    print("done gfs")
    store["gfs"] = df
