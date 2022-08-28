// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('ECN', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__("DMRN"), function() {
			frappe.route_options = {
			};
		frappe.set_route('Form','Design Modification Request Note',"new-design-modification-request-note-1");
		}, __("Create"));
	}
});
