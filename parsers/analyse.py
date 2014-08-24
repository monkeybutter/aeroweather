__author__ = 'SmartWombat'

import pandas as pd

df = pd.read_hdf('/Users/SmartWombat/Desktop/store.h5', 'metar')

print df.columns
print df.shape
print df.dtypes
