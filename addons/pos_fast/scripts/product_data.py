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
    vals = {
        'list_price': 100.0,
        'description': u'description',
        'display_name': 'Product Example - %s' % str(i),
        'name': 'Product Example - %s' % str(i),
        'pos_categ_id': 2,
        'to_weight': u'True',
        'description_sale': u'Description Sale'
    }
    models.execute_kw(database, uid, password, 'product.product', 'create', [vals])
    ("--- %s seconds ---" % (time.time() - start_time))
    print '-' * 100