import xmlrpclib
import json
import time

start_time = time.time()

database = 'bruce8'
login = 'admin'
password = '1'
url = 'http://localhost:8069'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(database, login, password, {})


models = xmlrpclib.ServerProxy(url + '/xmlrpc/object')


for i in range(10000, 100000):

    ids = models.execute_kw(database, uid, password, 'product.product', 'search', [[['available_in_pos', '=', True]]])
    for id in ids:
        product = models.execute_kw(database, uid, password, 'product.product', 'read', [id], {'fields': ['image', 'name']})
        models.execute_kw(database, uid, password, 'product.product', 'copy', [id], {'default': {
            'image': product['image'],
            'name': product['name'] + '_' + str(i),
        }})
    ("--- %s seconds ---" % (time.time() - start_time))
    print '-' * 100