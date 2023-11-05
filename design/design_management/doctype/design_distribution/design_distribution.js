// Copyright (c) 2023, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Distribution', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1 && frm.doc.entry_type == "Drawing Transfer"){
			cur_frm.set_intro("Drawings Printed and Sent to Respective Departments.", "blue");

			cur_frm.add_custom_button(__("Received Qty"), function() {
				let dialog = new frappe.ui.Dialog({
					title : __('To Receive Summary'),
					fields: [
						{
							fieldname: 'items', fieldtype: 'Table', label: __('To Receive Items'),
							fields: [
								{
									'fieldtype': 'Link',
									'read_only': 0,
									'fieldname': 'item_code',
									'options': 'Item',
									'label': __('Item Code'),
									'in_list_view': 1,
									'columns': 8
								}, 
								{
									'fieldtype': 'Data',
									'read_only': 0,
									'fieldname': 'qty',
									'label': __('Qty'),
									'in_list_view': 1,
									'columns': 2
								}
							],
							in_place_edit: true,
							data: [],
						}
					],
					primary_action_label: 'Received',
					primary_action: function() {
						//var values = dialog.get_values();
						var selected_items = dialog.fields_dict.items.grid.get_selected_children();
						var items = frm.doc.items
						for(var ditem = 0; ditem < selected_items.length; ditem++){
							for(var item = 0; item < items.length; item++){
								if(items[item].item_code == selected_items[ditem].item_code){
									if(selected_items[ditem].qty > (items[item].qty - items[item].received_qty)){
										frappe.throw('Qty cannot be greater than actual qty')
									}
									else{
										frappe.call({
											method: 'design.design_management.doctype.design_distribution.design_distribution.ping',
											args: {
												id: items[item].name,
												qty: selected_items[ditem].qty
											},
											callback: (r) => {
												if(r.message){
													console.log(r.message)
												}
											}
										})
										frappe.call({
											method: 'design.design_management.doctype.design_distribution.design_distribution.update_received_qty',
											args: {
												id: items[item].name,
												qty: selected_items[ditem].qty
											},
											callback: (r) => {
												if(r.message){
													frappe.msgprint('Qty Received')
												}
											}
										})
									}
								}
							}
						}
						cur_dialog.hide();
					},
					
				});
				frm.doc.items.forEach(d => {
					if (d.qty != d.received_qty) {
						dialog.fields_dict.items.df.data.push({
							'item_code': d.item_code,
							'qty': d.qty - d.received_qty
						});
					}
				});
				dialog.fields_dict.items.grid.refresh();
				dialog.show();
			}, __("Update"));
		}
	}
});
