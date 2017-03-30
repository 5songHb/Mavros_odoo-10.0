odoo.define('pos_fast_loading.models', function (require) {
    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var _t = core._t;

    var _super_posmodel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;
            var product_index = _.findIndex(this.models, function (model) {
                return model.model === "product.product";
            });
            if (product_index !== -1) {
                this.models.splice(product_index, 1);
            }
            return _super_posmodel.load_server_data.apply(this, arguments).then(function () {
                var records = new Model('pos.auto.cache').call('get_products', []);
                self.chrome.loading_message(_t('LOADING : ') + ' product.product', 1);
                return records.then(function (products) {
                    self.db.add_products(products);
                });
            });
        },
    });
    var _super_posmodel2 = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;
            var product_index = _.findIndex(this.models, function (model) {
                return model.model === "res.partner";
            });
            if (product_index !== -1) {
                this.models.splice(product_index, 1);
            }
            return _super_posmodel2.load_server_data.apply(this, arguments).then(function () {
                var records = new Model('pos.auto.cache').call('get_customers', []);
                self.chrome.loading_message(_t('LOADING : ') + ' res.partner', 1);
                // return for core loading
                self.models.push(
                    {
                        model: 'res.partner',
                        fields: ['name', 'street', 'city', 'state_id', 'country_id', 'vat', 'phone', 'zip', 'mobile', 'email', 'barcode', 'write_date'],
                        domain: [['customer', '=', true]]
                    }
                )
                return records.then(function (partners) {
                    self.partners = partners;
                    self.db.add_partners(partners);
                });
            });
        },

    })
});
