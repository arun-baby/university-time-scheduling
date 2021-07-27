from google.cloud import firestore

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.
db = firestore.Client.from_service_account_json('C:\\Users\\Acer\\Documents\\GitHub\\university-time-scheduling\\utp-320721-e1afef9ba011.json')

from time import time 

params = {}
params['EID'] = f'LS_{int(time())}'
params['BUDGET'] = 10
params['STOPPING_SP'] = 5000
params['type'] = 'Local Search'

doc_ref = db.collection('experiments').document(params['EID'])
doc_ref.set(params)