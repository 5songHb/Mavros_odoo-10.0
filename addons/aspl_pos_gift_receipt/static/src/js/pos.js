odoo.define('aspl_pos_gift_receipt.gift_receipt', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var chrome = require('point_of_sale.chrome');

var QWeb = core.qweb;
var _t = core._t;

    var GiftReceipt = screens.ActionButtonWidget.extend({
        template: 'GiftReceipt',
        button_click: function(){
            var order    = this.pos.get_order();
            var lines    = order.get_orderlines();
            if(lines.length > 0) {
                var selected_line = order.get_selected_orderline();
                if (selected_line) {
                    order.set_gift_receipt_mode(!order.get_gift_receipt_mode());
                	selected_line.set_line_for_gift_receipt(order.get_gift_receipt_mode());
                	if(order.get_gift_receipt_mode()){
                	    $(this.el).addClass('highlight');
                	} else {
                	    $(this.el).removeClass('highlight')
                	}
                }
            } else {
                $( ".order-empty" ).effect( "bounce", {}, 500 );
            }
        },
    });

    screens.define_action_button({
        'name': 'GiftReceipt',
        'widget': GiftReceipt,
        'condition': function(){
            return this.pos.config.enable_gift_receipt;
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            _super_orderline.initialize.call(this, attr, options);
        },
        set_line_for_gift_receipt: function(line_for_gift_receipt) {
            this.set('line_for_gift_receipt', line_for_gift_receipt);
        },
        get_line_for_gift_receipt: function() {
            return this.get('line_for_gift_receipt');
        },
        export_for_printing: function(){
            var new_val = {};
            var orderlines = _super_orderline.export_for_printing.call(this);
            new_val = {
            	gift_receipt: this.get_line_for_gift_receipt() || false,
            };
            $.extend(orderlines, new_val);
            return orderlines;
        },
    });

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            _super_Order.initialize.call(this, attributes,options);
            this.set({
                'gift_receipt_mode': false,
            })
        },
        set_gift_receipt_mode: function(gift_receipt_mode){
            this.set('gift_receipt_mode', gift_receipt_mode);
        },
        get_gift_receipt_mode: function() {
            return this.get('gift_receipt_mode');
        },
        add_product: function(product, options){
            var self = this;
            _super_Order.add_product.call(this, product, options);
            var selected_line = self.get_selected_orderline();
            if (selected_line){
                if(self.get_gift_receipt_mode()){
                    selected_line.set_line_for_gift_receipt(self.get_gift_receipt_mode());
                }
            }
        },
        generate_unique_id: function() {
            var timestamp = new Date().getTime();
            return Number(timestamp.toString().slice(-10));
        },
        export_for_printing: function(){
        	var new_val = {};
            var orders = _super_Order.export_for_printing.call(this);
            var order_no = this.get_name() || false;
            if(order_no && order_no.indexOf(_t('Order')) > -1){
        		order_no = order_no.replace(_t('Order '),'');
            }
            new_val = {
            	order_no: order_no,
            };
            $.extend(orders, new_val);
            return orders;
        },
    });
    screens.OrderWidget.include({
        click_line: function(orderline, event) {
            var self = this;
            var order = this.pos.get_order();
            this._super(orderline, event);
            var selected_line = order.get_selected_orderline();
            if(selected_line && selected_line.get_line_for_gift_receipt()){
                $('.gift_receipt_btn').addClass('highlight');
            } else {
                $('.gift_receipt_btn').removeClass('highlight');
            }
            order.set_gift_receipt_mode(selected_line.get_line_for_gift_receipt());
        },
        set_value: function(val) {
            this._super(val);
            var order = this.pos.get_order();
            var selected_line = order.get_selected_orderline();
            if (selected_line && selected_line.get_line_for_gift_receipt()) {
                order.set_gift_receipt_mode(true);
                $('.gift_receipt_btn').addClass('highlight');
            } else if(!selected_line || !selected_line.get_line_for_gift_receipt()){
                order.set_gift_receipt_mode(false);
                $('.gift_receipt_btn').removeClass('highlight');
            }
        },
    });

    var PosModel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		add_new_order: function(){
		    var order = PosModel.add_new_order.call(this);
		    if(order.get_gift_receipt_mode()){
		        $('.gift_receipt_btn').addClass('highlight');
		    } else {
		        $('.gift_receipt_btn').removeClass('highlight');
		    }
		    return order;
		},
	});

    chrome.OrderSelectorWidget.include({
        order_click_handler: function(event,$el) {
            this._super(event,$el);
            var order = this.pos.get_order();
            if(order.get_gift_receipt_mode()){
		        $('.gift_receipt_btn').addClass('highlight');
		    } else {
		        $('.gift_receipt_btn').removeClass('highlight');
		    }
        },

    });

    screens.ReceiptScreenWidget.include({
        show: function(){
            this._super();
            var self = this;
            var order = self.pos.get_order();
            if(order && order.get_name()){
            	var barcode_value = order.get_name();
                if (barcode_value.indexOf(_t("Order ")) != -1) {
                    var vals = barcode_value.split(_t("Order "));
                    if (vals) {
                        var barcode = vals[1];
                        $("tr#barcode1").html($("<td text-align:center;><div class='" + barcode + "' /></td>"));
                        $("." + barcode.toString()).barcode(barcode.toString(), "code128");
                        $("td#barcode_val").html(barcode);
                    }
                }
            }

        },
        render_receipt: function() {
            this._super();
            var order = this.pos.get_order();
            var gift_receipt_lines = _.filter(order.get_orderlines(), function(line){
                return line.get_line_for_gift_receipt()
            })
            if(gift_receipt_lines.length > 0){
                this.$('.pos-receipt-container').append(QWeb.render('PosGiftTicket',{
                    widget:this,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: gift_receipt_lines,
                }));
            }
        },
        print_xml: function() {
            var self = this;
            this._super();
            var env = {
                widget:  this,
                order: this.pos.get_order(),
                receipt: this.pos.get_order().export_for_printing(),
            };
            var receipt = QWeb.render('XmlGiftReceipt',env);

            this.pos.proxy.print_receipt(receipt);
            this.pos.get_order()._printed = true;
        },
    });

});