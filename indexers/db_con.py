"""
Get the db
"""

import json
import pymongo

with open('../db_creds.json', 'r') as cfile:
    creds = json.load(cfile)['cersei']

dbclient = pymongo.MongoClient("45.55.232.5:27017")
dbclient.cersei.authenticate(creds['u'], creds['p'], mechanism='MONGODB-CR')

db = dbclient.cersei
