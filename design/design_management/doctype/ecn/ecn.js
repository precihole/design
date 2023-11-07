// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('ECN', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__("Create DMRN"), function() {
				frappe.route_options = {
					'reference_no': frm.doc.name
				};
				frappe.set_route('Form','DMRN',"new-dmrn-1");
			});
		}
	}
});
