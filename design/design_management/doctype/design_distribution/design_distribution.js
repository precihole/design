// Copyright (c) 2023, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Distribution', {
	refresh: function(frm) {

		if(frm.doc.__islocal && frm.doc.reference_no){
			console.log('run')
			frappe.model.with_doc("DMRN", frm.doc.reference_no, function() {
				var mcd = frappe.model.get_doc("DMRN", frm.doc.reference_no);
					$.each(mcd.dmrn_details, function(i, d) {
					i = cur_frm.add_child("items");
					i.s_warehouse = 'Design';
					i.item_code = d.item_code;
					i.revision = d.new_revision;
				});
				cur_frm.refresh_field("items");
			});
		}

		var child = frm.doc.summary
		if(frm.doc.docstatus == 1 && frm.doc.entry_type == "Drawing Transfer"){
			cur_frm.set_intro("Drawings Printed and Sent to Respective Departments.", "blue");
			var remove_flag
			for(var item = 0; item < frm.doc.items.length; item++){
				if(frm.doc.items[item].qty == frm.doc.items[item].received_qty){
					remove_flag = 1
				}
				else{
					remove_flag = 0
				}
			}
			if(cur_frm.doc.summary.length > 0){
					
			cur_frm.add_custom_button(__("Drawing Discard"), function() {
				frappe.msgprint("djhdj")
			
					frappe.run_serially([
						() => frappe.new_doc('Design Distribution'),
						() => {
							cur_frm.set_value("entry_type","Drawing Discard"),
							cur_frm.set_value("drawing_discard", frm.doc.name)
		 
						},
						() => {
							//cur_frm.doc.stock_entry_type == 'Manufacture',
							cur_frm.clear_table('items')
							var len = child.length
							for(var i=0; i < len; i++){
								if ((child[i].qty - child[i].ordered_qty) > 0){
									cur_frm.add_child("items", { 
										item_code : child[i].item_code,
										qty : child[i].actual_qty,
										s_warehouse : child[i].t_warehouse,
										revision : child[i].revision
									})
								}
							}
						}
					], 
						//() => next action you want to perform
					);
			
		
			})
		}
			// console.log(remove_flag)
			// if(remove_flag == 0){
			// 	console.log(remove_flag)
			// 	cur_frm.add_custom_button(__("Received Qty"), function() {
			// 		let dialog = new frappe.ui.Dialog({
			// 			title : __('To Receive Summary'),
			// 			fields: [
			// 				{
			// 					fieldname: 'items', fieldtype: 'Table', label: __('To Receive Items'),
			// 					fields: [
			// 						{
			// 							'fieldtype': 'Link',
			// 							'read_only': 0,
			// 							'fieldname': 'item_code',
			// 							'options': 'Item',
			// 							'label': __('Item Code'),
			// 							'in_list_view': 1,
			// 							'columns': 8
			// 						}, 
			// 						{
			// 							'fieldtype': 'Data',
			// 							'read_only': 0,
			// 							'fieldname': 'qty',
			// 							'label': __('Qty'),
			// 							'in_list_view': 1,
			// 							'columns': 2
			// 						}
			// 					],
			// 					in_place_edit: true,
			// 					data: [],
			// 				}
			// 			],
			// 			primary_action_label: 'Received',
			// 			primary_action: function() {
			// 				//var values = dialog.get_values();
			// 				var selected_items = dialog.fields_dict.items.grid.get_selected_children();
			// 				var items = frm.doc.items
			// 				for(var ditem = 0; ditem < selected_items.length; ditem++){
			// 					for(var item = 0; item < items.length; item++){
			// 						if(items[item].item_code == selected_items[ditem].item_code){
			// 							if(selected_items[ditem].qty > (items[item].qty - items[item].received_qty)){
			// 								frappe.throw('Qty cannot be greater than actual qty')
			// 							}
			// 							else{
			// 								frappe.call({
			// 									method: 'design.design_management.doctype.design_distribution.design_distribution.create_dle_entry',
			// 									args: {
			// 										item_code: items[item].item_code,
			// 										warehouse: 'Transit',
			// 										doctype: frm.doc.doctype,
			// 										id: frm.doc.name,
			// 										qty: selected_items[ditem].qty,
			// 										flag: 0
	
			// 									},
			// 									callback: (r) => {
			// 										if(r.message){
			// 											console.log(r.message)
			// 										}
			// 									}
			// 								})
			// 								frappe.call({
			// 									method: 'design.design_management.doctype.design_distribution.design_distribution.create_dle_entry',
			// 									args: {
			// 										item_code: items[item].item_code,
			// 										warehouse: items[item].t_warehouse,
			// 										doctype: frm.doc.doctype,
			// 										id: frm.doc.name,
			// 										qty: selected_items[ditem].qty,
			// 										flag: 1
	
			// 									},
			// 									callback: (r) => {
			// 										if(r.message){
			// 											console.log(r.message)
			// 										}
			// 									}
			// 								})
			// 								frappe.call({
			// 									method: 'design.design_management.doctype.design_distribution.design_distribution.update_received_qty',
			// 									args: {
			// 										id: items[item].name,
			// 										qty: selected_items[ditem].qty
			// 									},
			// 									callback: (r) => {
			// 										if(r.message){
			// 											frappe.msgprint('Qty Received')
			// 										}
			// 									}
			// 								})
			// 							}
			// 						}
			// 					}
			// 				}
			// 				cur_dialog.hide();
			// 			},
			// 		});
			// 		frm.doc.items.forEach(d => {
			// 			if (d.qty != d.received_qty) {
			// 				dialog.fields_dict.items.df.data.push({
			// 					'item_code': d.item_code,
			// 					'qty': d.qty - d.received_qty
			// 				});
			// 			}
			// 		});
			// 		dialog.fields_dict.items.grid.refresh();
			// 		dialog.show();
			// 	}, __("Update"));
			// }
		}
	}
});
