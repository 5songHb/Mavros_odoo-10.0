odoo.define('pos_prod_load_background.pos', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var chrome = require('point_of_sale.chrome');
	var core = require('web.core');
	var Model = require('web.DataModel');
	var device = require('point_of_sale.devices');
	var DB = require('point_of_sale.DB');

	var _t = core._t;
	var QWeb = core.qweb;

    models.load_fields("product.product", ['barcode_product_ids','write_date']);
    models.load_fields("res.partner", ['mobile']);

	models.PosModel.prototype.models.push({
    	model:  'res.users',
        fields: [ 'name','barcode'],
        loaded: function(self,users){
        	self.users = users; 
            self.db.add_users(users);
        },
	});
	// Multi Barcode Search
	models.PosModel.prototype.models.push({
	    model:  'product.barcode',
        fields: [],
        loaded: function(self, barocdes){
        	self.db.add_product_barcode(barocdes);
        },
    });

	var _super_posmodel = models.PosModel;
	models.PosModel = models.PosModel.extend({
		initialize: function(session, attributes) {
			_super_posmodel.prototype.initialize.call(this, session, attributes);
	            this.product_list = [];
	            this.product_fields = [];
	            this.product_domain = [];
	            this.product_context = {};
	            this.partner_fields = [];
	            this.partner_domain = [];
	    },
		fetch: function(model, fields, domain, ctx){
            this._load_progress = (this._load_progress || 0) + 0.05; 
            this.chrome.loading_message(('Loading')+' '+model,this._load_progress);
            return new Model(model).query(fields).filter(domain).context(ctx).all()
        },
        load_server_data: function(){
            var self = this;
            var loaded = new $.Deferred();
            var progress = 0;
            var progress_step = 1.0 / self.models.length;
            var tmp = {}; // this is used to share a temporary state between models loaders

            function load_model(index){
        	    var model = self.models[index];
                if(index >= self.models.length){
                    loaded.resolve();
                }else{
                    var model = self.models[index];
                    var cond = typeof model.condition === 'function'  ? model.condition(self,tmp) : true;
                    if (!cond) {
                        load_model(index+1);
                        return;
                    }

                    var fields =  typeof model.fields === 'function'  ? model.fields(self,tmp)  : model.fields;
                    var domain =  typeof model.domain === 'function'  ? model.domain(self,tmp)  : model.domain;
                    var context = typeof model.context === 'function' ? model.context(self,tmp) : model.context; 
                    var ids     = typeof model.ids === 'function'     ? model.ids(self,tmp) : model.ids;
                    var order   = typeof model.order === 'function'   ? model.order(self,tmp):    model.order;
                    if ( model.model && $.inArray(model.model,['product.product', 'res.partner']) == -1) {
                        self.chrome.loading_message(_t('Loading')+' '+(model.label || model.model || ''), progress);
                    } else if(model.model && model.model == 'product.product') {
                        self.product_domain = self.product_domain.concat(model.domain);
                        self.product_fields = self.product_fields.concat(model.fields);
                        self.product_context = $.extend(self.product_context, context)
                    } else if(model.model && model.model == 'res.partner') {
                    	self.partner_fields = self.partner_fields.concat(model.fields);
                    	self.partner_domain = self.partner_domain.concat(model.domain);
                    }
                    progress += progress_step;
                   
                    var records;
                    if( model.model && $.inArray(model.model,['product.product', 'res.partner']) == -1){
                        if (model.ids) {
                            records = new Model(model.model).call('read',[ids,fields],context);
                        } else {
                            records = new Model(model.model)
                                .query(fields)
                                .filter(domain)
                                .order_by(order)
                                .context(context)
                                .all();
                        }
                        records.then(function(result){
                                try{    // catching exceptions in model.loaded(...)
                                    $.when(model.loaded(self,result,tmp))
                                        .then(function(){ load_model(index + 1); },
                                              function(err){ loaded.reject(err); });
                                }catch(err){
                                    console.error(err.stack);
                                    loaded.reject(err);
                                }
                            },function(err){
                                loaded.reject(err);
                            });
                    } else if ( model.loaded ){
                        try{    // catching exceptions in model.loaded(...)
                            $.when(model.loaded(self,tmp))
                                .then(  function(){ load_model(index +1); },
                                        function(err){ loaded.reject(err); });
                        }catch(err){
                            loaded.reject(err);
                        }
                    }else{
                        load_model(index + 1);
                    }
                }
            }

            try{
                load_model(0);
            }catch(err){
                loaded.reject(err);
            }
            return loaded;
       },
       load_new_partners: function(){
    	   var self = this;
    	   var def  = new $.Deferred();
    	   if(self.partners_load){
	           var fields = self.partner_fields ? self.partner_fields :
   	            ['name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date'];
	           new Model('res.partner')
	               .query(fields)
	               .filter([['customer','=',true],['write_date','>',this.db.get_partner_write_date()]])
	               .all({'timeout':3000, 'shadow': true})
	               .then(function(partners){
	                   if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
	                       def.resolve();
	                   } else {
	                       def.reject();
	                   }
	               }, function(err,event){ event.preventDefault(); def.reject(); });
	           return def;
    	   }
    	   return def;
       },
       scan_product: function(parsed_code){ //Multi Barcode Search
            var self = this;
            var selectedOrder = this.get_order();
            var res = _super_posmodel.prototype.scan_product.call(this, parsed_code);
            if(!res){
                var product_id = self.db.get_product_id_by_barcode_name(parsed_code.code);
                if (product_id){
                    var product = self.db.get_product_by_tmpl_id(product_id[0]);
                    if (product){
                        selectedOrder.add_product(product);
                        return true;
                    }
                }
            }
            return res;
	   },
	});

	screens.ProductCategoriesWidget.include({
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            var model = new Model("product.product");
            new Model("product.product").call("calculate_product").then(function(result) {
            	$('div.product_progress_bar').css('display','');
			    if(result && result[0]){
			    	var total_products = parseInt(result[0][0]);
			    	var remaining_time;
			    	if(total_products){
			    		var product_limit = 1000;
			    		var count_loop = total_products;
			    		var count_loaded_products = 0;
			    		function ajax_product_load(){
			    			if(count_loop > 0){
			    				$.ajax({
					                type: "GET",
						            url: '/web/dataset/load_products',
						            data: {
						                    model: 'product.product',
						                    fields: JSON.stringify(self.pos.product_fields),
						                    domain: JSON.stringify(self.pos.product_domain),
						                    context: JSON.stringify(self.pos.product_context),
						                    product_limit:product_limit,
						                },
						            success: function(res) {
						            		var all_products = JSON.parse(res)
						            		count_loop -= JSON.parse(res).length;
						            		remaining_time = ((total_products - count_loop) / total_products) * 100;
//						            		$('#bar').css({'width': +remaining_time+'% !important'});
							            	product_limit += 1000;
							            	all_products.map(function(product){
                                           		self.pos.product_list.push(product);
                                       		});
							                self.pos.db.add_products(JSON.parse(res));
							                self.renderElement();
							                $('div.product_progress_bar').css('display','');
						            		$('.product_progress_bar').find('#bar').css('width', parseInt(remaining_time)+'%', 'important');
						            		$('.product_progress_bar').find('#progress_status').html(parseInt(remaining_time) + "% completed");
						            		count_loaded_products += all_products.length;
                                       		all_products = [];
           									if(count_loaded_products >= total_products){
												self.pos.db.set_is_product_load(true);
												$('.product_progress_bar').delay(3000).fadeOut('slow');
           									}
							                ajax_product_load()
						            },
						            error: function() {
						                $('.product_progress_bar').find('#bar').css('width', '100%', 'important');
					            		$('.product_progress_bar').find('#progress_status').html("Products loading failed...");
						            },
					            });
			    			}
			    		}
			    		ajax_product_load();
			    	}else{
			    		alert("Can't calculate products...");
			    	}
			    }
			});
	    },
	    perform_search: function(category, query, buy_result){
	        var products;
	        var self = this;
	        if(query){
	            products = this.pos.db.search_product_in_category(category.id, query);
	            if(buy_result && products.length === 1){
                    this.pos.get_order().add_product(products[0]);
                    this.clear_search();
	            }else if(products.length === 0 && buy_result){
//	            	if(self.pos.product_list.length > 0){
                        //Multi Barcode Search
	            		var product_barcode_ids = []
	            		product_barcode_ids.push(self.pos.db.get_barcode_id_by_name(query));
	            		var domain = [['sale_ok','=',true],['available_in_pos','=',true], '|', '|', '|', ['name', 'ilike', query], ['default_code', 'ilike', query], ['barcode', 'ilike', query], ['barcode_product_ids', 'in', product_barcode_ids]];
	                	var model = new Model("product.product");
	            		var fields = ['display_name', 'list_price', 'lst_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
	            		                 'to_weight', 'uom_id', 'description_sale', 'description',
	            		                 'product_tmpl_id', 'barcode_product_ids','tracking'];
	            		var context = {
	                            'pricelist': self.pos.pricelist.id,
	                            'display_default_code': false,
	                        }
	            		var offset;
	            		model.call("search_read", [domain=domain, fields=fields, offset=0, false, false, context=context]).pipe(
	                        function(result) {
	                        	if(result.length > 0){
	                        		if(self.pos.product_list.length != undefined){
	                        			self.pos.product_list = result;
	                	                self.pos.db.add_products(result);
	                        		}
	                        		self.chrome.screens.products.product_list_widget.set_product_list(result);
	                        		self.pos.get_order().add_product(result[0]);
	                        		self.clear_search();
	                        	}else {
	                        		self.chrome.screens.products.product_list_widget.set_product_list(result);
	                        		return console.info("Products not found.");
	                        	}
	                        }).fail(function (error, event){
	    						if(error.code === -32098) {
	    				        	event.preventDefault();
	    			           }
	    			       });
//	            	}else{
//	            		alert("Please wait products are loading.");
//	            	}
	            }else{
	                this.product_list_widget.set_product_list(products);
	            }
	        }else{
	            products = this.pos.db.get_product_by_category(this.category.id);
	            this.product_list_widget.set_product_list(products);
	        }
	    },
	});

	var SuperScreenWidget = screens.ScreenWidget.prototype;
	screens.ClientListScreenWidget.include({
		init: function(parent, options){
			var self = this;
			this._super(parent, options);
			self.pos.partners_load = false;
			$.ajax({
	            type: "GET",
	            url: '/web/dataset/load_customers',
	            data: {
	                model: 'res.partner',
	                domain:JSON.stringify(self.pos.partner_domain),
                    fields: JSON.stringify(self.pos.partner_fields)
                },
	            success: function(res) {
	                self.pos.partners = JSON.parse(res);
	                self.pos.partners_load = true;
	                $('.cust_loading').html('');
	                self.pos.db.add_partners(JSON.parse(res));
	                self.render_list(self.pos.db.get_partners_sorted(1000));
	            },
	            error: function() {
	                console.log('Partner Qa-run failed.');
	            },
	        });
		},
		show: function(){
			var self = this;
			SuperScreenWidget.show.call(this);

			this.renderElement();
	        this.details_visible = false;
	        this.old_client = this.pos.get_order().get_client();

	        this.$('.back').click(function(){
	            self.gui.back();
	        });

	        this.$('.next').click(function(){   
	            self.save_changes();
	            self.gui.back();    // FIXME HUH ?
	        });

	        this.$('.new-customer').click(function(){
	            self.display_client_details('edit',{
	                'country_id': self.pos.company.country_id,
	            });
	        });

	        var partners = this.pos.db.get_partners_sorted(1000);
	        if(this.pos.partners_load){
	        	this.render_list(partners);
	        } else {
	        	this.render_list([]);
	        	self.pos.partners = [];
	        }
	        

	        if(partners.length > 0){
	        	this.reload_partners();
	        }

	        if( this.old_client ){
	            this.display_client_details('show',this.old_client,0);
	        }

	        this.$('.client-list-contents').delegate('.client-line','click',function(event){
	            self.line_select(event,$(this),parseInt($(this).data('id')));
	        });

	        var search_timeout = null;

	        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
	            this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
	        }

	        this.$('.searchbox input').on('keypress',function(event){
	            clearTimeout(search_timeout);

	            var query = this.value;

	            search_timeout = setTimeout(function(){
	                self.perform_search(query,event.which === 13);
	            },70);
	        });

	        this.$('.searchbox .search-clear').click(function(){
	            self.clear_search();
	        });
		},
		render_list: function(partners){
			var self = this;
	        var contents = this.$el[0].querySelector('.client-list-contents');
	        contents.innerHTML = "";
	        if(partners.length > 0 || this.pos.partners_load){
		        for(var i = 0, len = Math.min(partners.length,1000); i < len; i++){
		            var partner    = partners[i];
		            var clientline = this.partner_cache.get_node(partner.id);
		            if(!clientline){
		                var clientline_html = QWeb.render('ClientLine',{widget: this, partner:partners[i]});
		                var clientline = document.createElement('tbody');
		                clientline.innerHTML = clientline_html;
		                clientline = clientline.childNodes[1];
		                this.partner_cache.cache_node(partner.id,clientline);
		            }
		            if( partner === this.old_client ){
		                clientline.classList.add('highlight');
		            }else{
		                clientline.classList.remove('highlight');
		            }
		            contents.appendChild(clientline);
		        }
	        }else{
	        	contents.innerHTML = "<td colspan='5' style='background-color: white;'><div id='partner_loading' align='center' style='background-color: white;padding-top: 70px;font-size:20px;vertical-align:middle;'>" +
        		"<img src='/pos_prod_load_background/static/src/img/loader.gif/' /><br/>Loading...</div></td>";
	        }
	    },
	    perform_search: function(query, associate_result){
	        var customers;
	        var self = this;
	        if(query){
	            customers = this.pos.db.search_partner(query);
	            var customer_load = this.pos.db.get_partners_sorted();
	            this.display_client_details('hide');
	            if ( associate_result && customers.length === 1){
	                this.new_client = customers[0];
	                this.save_changes();
	                this.gui.back();
	            }else if(associate_result && (customer_load.length == 0 || !self.pos.partners_load)){
//	            	call when customers are loading and cashier want to search customer
                    var domain = [['customer', '=', true],'|', '|',['name', 'ilike', query], ['phone', '=', query], ['mobile', '=', query]];
                	var model = new Model("res.partner");
            		var fields = self.pos.partner_fields ? self.pos.partner_fields :
            			['name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date'];
            		model.call("search_read", [domain=domain, fields=fields])
            		.then(function(result) {
                        	if(result.length > 0){
//                        		if(self.pos.partners.length == 0 || self.pos.partners.length == undefined){
                        			self.pos.partners = result;
                	                self.pos.db.add_partners(result);
                	                self.render_list(result);
//                        		}
                        	}else {
                        		return console.info("Customer not found.");
                        	}
                        }).fail(function (error, event){
    						if(error.code === -32098) {
    				        	event.preventDefault();
    			           }
    			       });
	            }/*else if(customers.length === 0 && (customer_load.length != 0 || self.pos.partners_load)){
	            	alert("else iffffff");
//	            	call when customers are loaded and if new customer created in backend

	            	var domain = [['name', 'ilike', query],['customer', '=', true]];
                	var model = new Model("res.partner");
//            		var domain = [['customer', '=', true],['dob', '=', date]]
            		var fields = ['name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date'];
            		model.call("search_read", [domain=domain, fields=fields]).pipe(
                        function(result) {
                        	if(result.length > 0){
                        		if(self.pos.partners != undefined){
                        			self.pos.partners = result;
                	                self.pos.db.add_partners(result);
                        		}
                        		self.render_list(result);
                        	}else {
                        		return console.info("Customer Not Found");
                        	}
                        }).fail(function (error, event){
    						if(error.code === -32098) {
    				        	event.preventDefault();
    			           }
    			       });
	            }*/else {
	            	this.render_list(customers);
	            }
	        }else{
	            customers = this.pos.db.get_partners_sorted();
	            this.render_list(customers);
	        }
	    },
	});

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		init_from_JSON: function(json) {
			var self = this;
	        var client;
	        this.sequence_number = json.sequence_number;
	        this.pos.pos_session.sequence_number = Math.max(this.sequence_number+1,this.pos.pos_session.sequence_number);
	        this.session_id    = json.pos_session_id;
	        this.uid = json.uid;
	        this.name = _t("Order ") + this.uid;
	        this.validation_date = json.creation_date;

	        if (json.fiscal_position_id) {
	            var fiscal_position = _.find(this.pos.fiscal_positions, function (fp) {
	                return fp.id === json.fiscal_position_id;
	            });

	            if (fiscal_position) {
	                this.fiscal_position = fiscal_position;
	            } else {
	                console.error('ERROR: trying to load a fiscal position not available in the pos');
	            }
	        }

//			set customer after refresh pos, if partner_id stored in cache then customer set into current order

	        if (json.partner_id) {
	        	new Model("res.partner").get_func("search_read")([['id', '=', json.partner_id]]).then(
	        		function(result) {
	        			if(result && result[0]){
	        				client = result[0];
	        				self.set_client(client);
	        			}else{
	        				client = null;
	        				self.set_client(client);
	        			}
	        		});
//	            client = this.pos.db.get_partner_by_id(json.partner_id);
//	            if (!client) {
//	                console.error('ERROR: trying to load a parner not available in the pos');
//	            }
	        } else {
	            client = null;
	        }
	        this.set_client(client);

	        this.temporary = false;     // FIXME
	        this.to_invoice = false;    // FIXME

//			when pos reload then skip stored orderlines and paymentlines

//	        var orderlines = json.lines;
//	        for (var i = 0; i < orderlines.length; i++) {
//	            var orderline = orderlines[i][2];
//	            this.add_orderline(new exports.Orderline({}, {pos: this.pos, order: this, json: orderline}));
//	        }

//	        var paymentlines = json.statement_ids;
//	        for (var i = 0; i < paymentlines.length; i++) {
//	            var paymentline = paymentlines[i][2];
//	            var newpaymentline = new exports.Paymentline({},{pos: this.pos, order: this, json: paymentline});
//	            this.paymentlines.add(newpaymentline);
//
//	            if (i === paymentlines.length - 1) {
//	                this.select_paymentline(newpaymentline);
//	            }
//	        }
	    },
	});

	device.BarcodeReader.include({
		scan: function(code){
            self = this;
            if(code.length > 3){
                if (!self.pos.db.get_is_product_load()) {
                    var product_barcode_ids = []
	            	product_barcode_ids.push(self.pos.db.get_barcode_id_by_name(code));
                    var fields = ['display_name', 'list_price','lst_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code',
                                  'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                                  'product_tmpl_id', 'tracking'];
                    //Multi Barcode Search
                    var domain = ['|','|', '|',['barcode', '=', code],['barcode', '=', '0'+code], ['barcode_product_ids', 'in', product_barcode_ids], ['default_code', '=', code]];
                    var context = {
                        pricelist: self.pos.pricelist.id,
                        display_default_code: false,
                    }
                    var offset;
                    new Model("product.product").get_func("search_read")(domain=domain, fields=fields, offset=0, false, false, context=context)
                        .then(function(result) {
                            if (result[0]) {
                                self.pos.get_order().add_product(result[0]);
                            } else {
                                var partner = self.pos.db.get_partner_by_barcode(code);
                                var cashier = self.pos.db.get_user_by_barcode(code);
                                if(code.length == 12){
                                    partner = self.pos.db.get_partner_by_barcode('0'+code);
                                    cashier = self.pos.db.get_user_by_barcode('0'+code);
                                }
                                if(partner) {
                                    self.pos.get('selectedOrder').set_client(partner);
                                }else if(cashier) {
                                    var usernameWidget_obj = new chrome.UsernameWidget(self, {});
                                    self.pos.cashier = {};
                                    self.pos.cashier['id'] = cashier.id;
                                    self.pos.cashier['name'] = cashier.name;
                                    $('.username').html(self.pos.cashier['name']);
                                } else {
                                    var partner = self.pos.db.get_partner_by_barcode(code);
                                    var cashier = self.pos.db.get_user_by_barcode(code);
                                    if(partner) {
                                        self.pos.get_order().set_client(partner);
                                    }else if(cashier) {
                                        var usernameWidget_obj = new chrome.UsernameWidget(self, {});
                                        self.pos.cashier = {};
                                        self.pos.cashier['id'] = cashier.id;
                                        self.pos.cashier['name'] = cashier.name;
                                        $('.username').html(self.pos.cashier['name']);
                                    } else {
                                        var parse_result = {
                                            encoding: 'error',
                                            type: 'error',
                                            code: code,
                                        }
                                        if(parse_result.type in {'product':'', 'weight':'', 'price':''}){    //ean is associated to a product
                                            if(self.action_callback['product']){
                                                self.action_callback['product'](parse_result);
                                            }
                                        }else{
                                            if(self.action_callback[parse_result.type]){
                                                self.action_callback[parse_result.type](parse_result);
                                            }
                                        }
                                    }
                                }
                            }
                        });
                } else {
                    this._super(code, this);
                }
            }
        },
    });

	DB.include({
		init: function(options){
			this.user_by_barcode = {};
			this.barcode_by_id = {};
			this.product_write_date = null;
			this.barcode_write_date = null;
			this.barocde_id_by_name = [];
			this.product_id_by_barcode_name = [];
			this.product_by_templ_id = [];
			this.is_product_load = false;
			this._super(options,this);
		},
		add_users: function(users){
            for(var i = 0, len = users.length; i < len; i++){
                var user = users[i];
                if(user.barcode){
                    this.user_by_barcode[user.barcode] = user;
                }
            }
        },
        get_user_by_barcode: function(barcode){
            return this.user_by_barcode[barcode];
        },
        add_products: function(products){
            var stored_categories = this.product_by_category_id;
            var new_write_date = '';
            var product;
            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
//                if(product.lst_price){
//                    product.price = product.lst_price;
//                } else {
//                    product.price = product.list_price;
//                }

                if(this.get_product_by_id(product.id)){
                    continue;
                }
                var search_string = this._product_search_string(product);
                var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : this.root_category_id;
                product.product_tmpl_id = product.product_tmpl_id[0];
                if(!stored_categories[categ_id]){
                    stored_categories[categ_id] = [];
                }
                stored_categories[categ_id].push(product.id);

                if(this.category_search_string[categ_id] === undefined){
                    this.category_search_string[categ_id] = '';
                }
                this.category_search_string[categ_id] += search_string;

                var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                for(var j = 0, jlen = ancestors.length; j < jlen; j++){
                    var ancestor = ancestors[j];
                    if(! stored_categories[ancestor]){
                        stored_categories[ancestor] = [];
                    }
                    stored_categories[ancestor].push(product.id);

                    if( this.category_search_string[ancestor] === undefined){
                        this.category_search_string[ancestor] = '';
                    }
                    this.category_search_string[ancestor] += search_string;
                }

                this.product_by_id[product.id] = product;
                this.product_by_templ_id[product.product_tmpl_id] = product;
                if(product.barcode){
                    this.product_by_barcode[product.barcode] = product;
                }
                if (    this.product_write_date &&
                            this.product_by_id[product.id] &&
                            new Date(this.product_write_date).getTime() + 1000 >=
                            new Date(product.write_date).getTime() ) {
                        // FIXME: The write_date is stored with milisec precision in the database
                        // but the dates we get back are only precise to the second. This means when
                        // you read partners modified strictly after time X, you get back partners that were
                        // modified X - 1 sec ago.
                        continue;
                } else if ( new_write_date < product.write_date ) {
                    new_write_date  = product.write_date;
                }
            }
            this.product_write_date = new_write_date || this.product_write_date;
        },
//        add_products: function(products){
//        	var self = this;
//        	this._super(products);
//        	var product;
//        	var new_write_date = '';
//        	if(products && products.length > 0){
//        		for(var i = 0, len = products.length; i < len; i++){
//        			product = products[i];
//
//        		}
//        		this.product_write_date = new_write_date || this.product_write_date;
//        	}
//        },
        get_product_by_tmpl_id: function(tmpl_id){
            return this.product_by_templ_id[tmpl_id];
        },
        get_product_write_date: function(){
            return this.product_write_date || "1970-01-01 00:00:00";
        },
        get_barcode_write_date: function(){
            return this.barcode_write_date || "1970-01-01 00:00:00";
        },
        //Multi Barcode Search
        add_product_barcode: function(barcodes){
            var self = this;
            var new_write_date = '';

            for(var i=0; i<barcodes.length; i++){
                var barcode = barcodes[i];
                self.barocde_id_by_name[barcode.barcode_product] = barcode.id;
                self.product_id_by_barcode_name[barcode.barcode_product] = barcode.product_tmpl_id;
                self.barcode_by_id[barcode.id] = barcode;

                if (    this.barcode_write_date &&
                        this.barcode_by_id[barcode.id] &&
                        new Date(this.barcode_write_date).getTime() + 1000 >=
                        new Date(barcode.write_date).getTime() ) {
                    // FIXME: The write_date is stored with milisec precision in the database
                    // but the dates we get back are only precise to the second. This means when
                    // you read partners modified strictly after time X, you get back partners that were
                    // modified X - 1 sec ago.
                    continue;
	            } else if ( new_write_date < barcode.write_date ) {
	                new_write_date  = barcode.write_date;
	            }
            }
            this.barcode_write_date = new_write_date || this.barcode_write_date;
        },
        get_barcode_id_by_name: function(name){
            return this.barocde_id_by_name[name];
        },
        get_barcode_by_id: function(id){
            return this.barcode_by_id[id];
        },
        get_product_id_by_barcode_name: function(name){
            return this.product_id_by_barcode_name[name];
        },
        remove_barcode_by_id: function(id){
        	var barcode = this.get_barcode_by_id(id);
        	if(barcode){
        		this.product_id_by_barcode_name[barcode.barcode_product] = 0;
        		this.barocde_id_by_name[barcode.barcode_product] = 0
        		this.barcode_by_id[barcode.id] = [];
        	}
        },
        search_product_in_category: function(category_id, query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.category_search_string[category_id]);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_product_by_id(id));
                }else{
                    var r1 = this.get_product_id_by_barcode_name(query);
                    if (r1){
                        var product = this.get_product_by_tmpl_id(r1[0]);
                        if (product){
                            results.push(product);
                        } else {
                            break;
                        }
                    }else{
                        break;
                    }
                    break;
                }
            }
            return results;
        },
		set_is_product_load: function(is_product_load) {
           this.is_product_load = is_product_load;
       },
		get_is_product_load: function(){
       	return this.is_product_load;
       },
	});

	var SyncProduct = screens.ActionButtonWidget.extend({
        template: 'SyncProduct',
        button_click: function(){
            var self = this;
            if(self.pos.product_list.length > 0 && self.pos.db.get_is_product_load()){
            	var context = { 
                        pricelist: self.pos.pricelist.id, 
                        display_default_code: false, 
                    }
            	var fields = ['display_name', 'lst_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
                         'to_weight', 'uom_id', 'description_sale', 'description',
                         'product_tmpl_id','tracking','write_date', 'barcode_product_ids'];
 	           var offset;
 	           var domain = [['write_date','>',self.pos.db.get_product_write_date()],['available_in_pos','=',true]];
 	           new Model('product.product').call("search_read", [domain=domain, fields=fields, offset=0, false, false, context=context]).pipe(
                   function(products) {
                	   if(products && products[0]){
                		   _.each(products, function(product){
                			   var old_product = self.pos.db.get_product_by_id(product.id)
                			   if (old_product){
                				   var removed_barcodes_id = [];
                				   jQuery.grep(old_product.barcode_product_ids, function(el) {
                					    if (jQuery.inArray(el, product.barcode_product_ids) == -1) removed_barcodes_id.push(el);
                					});
                				   _.each(removed_barcodes_id, function(id){
                					   self.pos.db.remove_barcode_by_id(id)
                				   })
                				   
                			   }
                		   })
	                		self.pos.db.add_products(products);
	                		products.map(function(product){
        						$("[data-product-id='"+product.id+"']").find('.price-tag').html(self.format_currency(product.lst_price));
        						$("[data-product-id='"+product.id+"']").find('.product-name').html(product.display_name);
        					});
	                	}
                   });
 	          new Model('product.barcode').call("search_read", [domain=[['write_date','>',self.pos.db.get_barcode_write_date()]], fields=[], 0, false, false, context={}]).pipe(
                   function(barcodes) {
                	   if(barcodes && barcodes[0]){
	                		self.pos.db.add_product_barcode(barcodes);
	                	}
                   });
            }else{
            	alert("Please wait, Products are still loading...");
            }
        },
    });
	screens.define_action_button({
        'name': 'SyncProduct',
        'widget': SyncProduct,
        'condition': function(){
            return false;
        },
    });

});