// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Printout Creation', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__("Design Tranfer"), function() {
			frappe.route_options = {
			};
		frappe.set_route('Form','DDN',"new-ddn-1");
		}, __("Create"));
	}
});
