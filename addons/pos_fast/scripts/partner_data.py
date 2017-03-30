import xmlrpclib
import json
import time

start_time = time.time()

database = 'bruce10_2'
login = 'admin'
password = 'admin'
url = 'http://localhost:8069'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(database, login, password, {})

models = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

for i in range(0, 10000):
    vals = {'phone': u'False', 'street': u'89 Lingfield Tower', 'write_date': u'2016-11-29 11:13:00',
            'city': u'London', 'name': 'POS customer example - %s' % str(i), 'zip': u'False', 'mobile': u'False',
            'country_id': 233, 'state_id': False, 'email': u'lucas.jones@thinkbig.example.com',
            'vat': u'False'}
    models.execute_kw(database, uid, password, 'res.partner', 'create', [vals])
    ("--- %s seconds ---" % (time.time() - start_time))
    print '-' * 100
