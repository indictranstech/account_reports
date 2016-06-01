// frappe.ui.form.on("Purchase Invoice Item","item_code",function(frm,cdt,cdn){
// 	items=locals[cdt][cdn]
// 	return frappe.call({
// 		method: "account_reports.custom_py.fetch_taxes",
// 		args:{
// 			item:items.item_code
// 		},
// 		callback: function(r) {
// 			if(r.message) {
//                 doc=frm.doc;
//                 if (frm.doc.__islocal==1){
// 					for(i=0;i<r.message.length;i++){
// 					    var taxes= frappe.model.add_child(doc, "Purchase Taxes and Charges", "taxes");
// 					    taxes.charge_type="On Net Total" ;
// 					    taxes.tax_code=r.message[i]['tax_code'];
// 					    taxes.account_head=r.message[i]['tax_type'];
// 					    // taxes.rate=r.message[i]['tax_rate'];
// 					    taxes.rate = 0.0
// 					}
// 				}
// 			}
// 		}
// 	})
// })

// frappe.ui.form.on("Sales Order Item","item_code",function(frm,cdt,cdn){
	
// 	items=locals[cdt][cdn]
// 	return frappe.call({
// 				method: "account_reports.custom_py.fetch_taxes",
// 				args:{
// 					item:items.item_code
// 				},
				
// 				callback: function(r) {
// 					if(r.message) {
// 						// console.log(JSON.stringify(r.message))


// 	                    doc=frm.doc;
// 	                    if (frm.doc.__islocal==1 )
// 	                    {
// 						for(i=0;i<r.message.length;i++)
// 						{
// 					   var taxes= frappe.model.add_child(doc, "Sales Taxes and Charges", "taxes");
// 					   taxes.charge_type="On Net Total" ;
// 					   taxes.tax_code=r.message[i]['tax_code'];
// 					   taxes.account_head=r.message[i]['tax_type'];
// 					   // taxes.rate=r.message[i]['tax_rate'];
// 						taxes.rate = 0.0	
// 						}
						
// 					}
// 				}
// 			}

// 			})

// })

//  frappe.ui.form.on("Sales Invoice Item","item_code",function(frm,cdt,cdn){
//  	console.log("Hiii")
// 	items=locals[cdt][cdn]
// 	return frappe.call({
// 				method: "account_reports.custom_py.fetch_taxes",
// 				args:{
// 					item:items.item_code
// 				},
				
// 				callback: function(r) {
// 					if(r.message) {
// 						// console.log(JSON.stringify(r.message))


// 	                    doc=frm.doc;
// 	                    if (frm.doc.__islocal==1 )
// 	                    {
// 						for(i=0;i<r.message.length;i++)
// 						{
// 					   var taxes= frappe.model.add_child(doc, "Sales Taxes and Charges", "taxes");
// 					   taxes.charge_type="On Net Total" ;
// 					   taxes.tax_code=r.message[i]['tax_code'];
// 					   taxes.account_head=r.message[i]['tax_type'];
// 					   // taxes.rate=r.message[i]['tax_rate'];
// 							taxes.rate = 0.0
// 						}
						
// 					}
// 				}
// 			}

// 			})

// })

//  frappe.ui.form.on("Purchase Order Item","item_code",function(frm,cdt,cdn){
// 	items=locals[cdt][cdn]
// 	return frappe.call({
// 				method: "account_reports.custom_py.fetch_taxes",
// 				args:{
// 					item:items.item_code
// 				},
				
// 				callback: function(r) {
// 					if(r.message) {
// 						// console.log(JSON.stringify(r.message))


// 	                    doc=frm.doc;
// 	                    if (frm.doc.__islocal==1 )
// 	                    {
// 						for(i=0;i<r.message.length;i++)
// 						{
// 					   var taxes= frappe.model.add_child(doc, "Purchase Taxes and Charges", "taxes");
// 					   taxes.charge_type="On Net Total" ;
// 					   taxes.tax_code=r.message[i]['tax_code'];
// 					   taxes.account_head=r.message[i]['tax_type'];
// 					   // taxes.rate=r.message[i]['tax_rate'];
// 							taxes.rate = 0.0
// 						}
						
// 					}
// 				}
// 			}

// 			})

// })
//  frappe.ui.form.on("Delivery Note Item","item_code",function(frm,cdt,cdn){
//  	console.log("Hiii")
// 	items=locals[cdt][cdn]
// 	return frappe.call({
// 				method: "account_reports.custom_py.fetch_taxes",
// 				args:{
// 					item:items.item_code
// 				},
				
// 				callback: function(r) {
// 					if(r.message) {
// 						// console.log(JSON.stringify(r.message))


// 	                    doc=frm.doc;
// 	                    if (frm.doc.__islocal==1 )
// 	                    {
// 						for(i=0;i<r.message.length;i++)
// 						{
// 					   var taxes= frappe.model.add_child(doc, "Sales Taxes and Charges", "taxes");
// 					   taxes.charge_type="On Net Total" ;
// 					   taxes.tax_code=r.message[i]['tax_code'];
// 					   taxes.account_head=r.message[i]['tax_type'];
// 					   // taxes.rate=r.message[i]['tax_rate'];
// 							taxes.rate = 0.0
// 						}
						
// 					}
// 				}
// 			}

// 			})

// })

//  frappe.ui.form.on("Purchase Receipt Item","item_code",function(frm,cdt,cdn){
// 	items=locals[cdt][cdn]
// 	return frappe.call({
// 				method: "account_reports.custom_py.fetch_taxes",
// 				args:{
// 					item:items.item_code
// 				},
				
// 				callback: function(r) {
// 					if(r.message) {
// 						// console.log(JSON.stringify(r.message))


// 	                    doc=frm.doc;
// 	                    if (frm.doc.__islocal==1 )
// 	                    {
// 						for(i=0;i<r.message.length;i++)
// 						{
// 					   var taxes= frappe.model.add_child(doc, "Purchase Taxes and Charges", "taxes");
// 					   taxes.charge_type="On Net Total" ;
// 					   taxes.tax_code=r.message[i]['tax_code'];
// 					   taxes.account_head=r.message[i]['tax_type'];
// 					   // taxes.rate=r.message[i]['tax_rate'];
// 							taxes.rate = 0.0
// 						}
						
// 					}
// 				}
// 			}

// 			})

// })