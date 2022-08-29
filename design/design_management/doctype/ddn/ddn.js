// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('DDN', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__('Stock Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.name,
					"from_date":frm.doc.posting_date,
					"to_date":frm.doc.posting_date
				};
				frappe.set_route("query-report", "Design Ledger");
			}, __("View"));
		}
	}
});
