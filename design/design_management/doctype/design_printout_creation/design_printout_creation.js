// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Printout Creation', {
	show_progress_for_items: function(frm) {
		var bars = [];
		var message = '';
		var added_min = false;

		// produced qty
		var title = __('Drawing Transferred', [10]);
		bars.push({
			'title': title,
			'width': (50) + '%',
			'progress_class': 'progress-bar-inverse'
		});
		message = title;
		frm.dashboard.add_progress(__('Status'), bars, message);
	},
	//refresh
	refresh: function(frm) {
	
		frm.trigger("show_progress_for_items");

		if(frm.doc.docstatus == 1){
			
			frm.add_custom_button(__('Stock Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.name
				};
				frappe.set_route("query-report", "Design Ledger Report");
			}, __("View"));
		}
		// if(frm.doc.docstatus == 1){
		// 	cur_frm.add_custom_button(__("Create Design Transfer"), function() {
		// 		frappe.route_options = {
					
		// 		};
		// 	frappe.set_route('Form','DDN',"new-ddn-1");
		// 	});
		// }
		if(frm.doc.__islocal && frm.doc.reference_no){
			frappe.model.with_doc("DMRN", frm.doc.reference_no, function() {
				var mcd = frappe.model.get_doc("DMRN", frm.doc.reference_no);
				frm.clear_table("item");
					$.each(mcd.dmrn_details, function(i, d) {
					i = frm.add_child("item");
					i.item_code = d.drawing_no;
					i.revision = d.rev_no
					});
				frm.refresh_field("item");
			});
		}
	}
});
// frappe.ui.form.on('Design Printout Item', {
// 	after_save : function(frm,cdt,cdn){
// 		var child = locals[cdt][cdn];
// 		var revison = child.revision;
// 		frappe.msgprint(revison)
// 		// var revision_validate = new RegExp("(^[A-Z]{1}[0-9]{1})$");
// 		// if (revision_validate.test(revison) === false){
// 		// 	frappe.msgprint(__("Incorrect Revision No"));
// 		// 	frappe.validated = false;
// 		// }
// 	}
// });
frappe.ui.form.on('Design Printout Creation', {
	validate: function(frm) {
		$.each(frm.doc.item || [], function(i, d) {
			var revision = d.revision;
			var revision_validate = new RegExp("(^[A-Z]{1}[0-9]{1,2})$");
			if(revision_validate.test(revision) === false){
				msgprint("<b>Incorrect Revision No</b>");
				frappe.validated = false;
			}
		})
	}
});
frappe.ui.form.on('Design Printout Creation', {
	stock_entry_type: function(frm) {
		frm.clear_table("item");
		frm.refresh_fields();	
	}
});
frappe.ui.form.on('Design Printout Item', {
	item_add: function(frm) {
		if(!frm.doc.stock_entry_type){
			frm.clear_table("item");
			frm.refresh_fields("item");
			frappe.msgprint("Select Entry Type First")
		}
		// if(frm.doc.stock_entry_type == "Drawing Creation"){
		// 	frm.clear_table("item");
		// 	var childTable = frm.add_child("item");
		// 	childTable.target_warehouse="Design"
		// 	cur_frm.refresh_fields("item");
		// }
		// else if(frm.doc.stock_entry_type == "Drawing Discard"){
		// 	frm.clear_table("item");
		// 	var childTable = frm.add_child("item");
		// 	childTable.target_warehouse="Scrap"
		// 	cur_frm.refresh_fields("item");
		// }
		if(frm.doc.stock_entry_type == "Design Transfer"){
			frm.clear_table("item");
			var childTable = frm.add_child("item");
			childTable.source_warehouse="Design"
			cur_frm.refresh_fields("item");
		}
		//else{
		// 	var childTable = frm.add_child("item");
		// 	childTable.source_warehouse="Design"
		// 	cur_frm.refresh_fields("item");
		// }
		// else if(frm.doc.stock_entry_type == "Drawing Receipt Confirmation"){
		// 	frm.clear_table("item");
		// 	var childTable = frm.add_child("item");
		// 	childTable.source_warehouse="Transit"
		// 	cur_frm.refresh_fields("item");
		// }
	}
});
// frappe.ui.form.on('Design Printout Item', {
// 	item_code: function(frm,cdt,cdn) {
// 		var c = locals[cdt][cdn];
// 		let d = new frappe.ui.Dialog({
// 			title: 'Select Revision Numbers',
// 			fields: [
// 				{
// 					label: 'Item Code',
// 					fieldname: 'item_code',
// 					fieldtype: 'Link',
// 					options: 'Item',
// 					default: c.item_code,
// 					read_only: 1

// 				},
// 				{
// 					label: 'Source Warehouse',
// 					fieldname: 'source_warehouse',
// 					fieldtype: 'Link',
// 					options: 'Design Warehouse',
// 					default: c.source_warehouse
// 				},
// 				{
// 					label: '',
// 					fieldname: 	'column_break_3',
// 					fieldtype: 'Column Break'
// 				},
// 				{
// 					label: 'Selected Qty',
// 					fieldname: 'qty',
// 					fieldtype: 'Float',
// 					default: '0',
// 					read_only: 1
// 				},
// 				{
// 					label: 'Revisions',
// 					fieldname: 	'section_break_7',
// 					fieldtype: 'Section Break'
// 				},
// 				{
// 					label: 'Selected Qty',
// 					fieldname: 'qty',
// 					fieldtype: 'Float',
// 					default: '0',
// 					read_only: 1
// 				}
// 				{
// 					label: 'Selected Qty',
// 					fieldname: 'qty',
// 					fieldtype: 'Float',
// 					default: '0',
// 					read_only: 1
// 				}
// 			],
// 			primary_action_label: 'Submit',
// 			primary_action(values) {
// 				console.log(values);
// 				d.hide();
// 			}
// 		});
		
// 		d.show();
// 	}
// });
