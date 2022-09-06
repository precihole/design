// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Printout Creation', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__("Design Transfer"), function() {
				frappe.route_options = {
					
				};
			frappe.set_route('Form','DDN',"new-ddn-1");
			}, __("Create"));
		}
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
