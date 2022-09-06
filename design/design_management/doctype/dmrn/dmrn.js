// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('DMRN', {
	refresh: function(frm) {
		if(frm.doc.__islocal){
			if(frm.doc.originator === undefined){
				cur_frm.set_value('originator', frappe.session.user);
			}   
		}
		if(frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__("Design Printout"), function() {
				frappe.route_options = {
					'reference_no':frm.doc.name
				};
			frappe.set_route('Form','Design Printout Creation',"new-design-printout-creation-1");
			}, __("Create"));
		}
		if(frm.doc.__islocal && frm.doc.reference_no){
			frappe.call({
				async: false,
				method: "frappe.client.get",
				args: {
					"doctype": "ECN",
					"filters": {
					'name': frm.doc.reference_no // where Clause 
					},
					"fieldname": ['item_code'] // fieldname to be fetched
				},
				callback: function (res) {
					if (res.message !== undefined) {
						var val=res.message;
						var item_code = val.item_code
						frm.clear_table("dmrn_details")
						var childTable = frm.add_child("dmrn_details");
						childTable.drawing_no=item_code
						cur_frm.refresh_fields("dmrn_details");
					}
				}
			})
		}		
	}
});
