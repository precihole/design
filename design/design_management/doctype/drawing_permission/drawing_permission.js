// Copyright (c) 2024, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Drawing Permission', {
	refresh: function(frm) {
		if (frm.doc.item_code && !frm.doc.file_url){
			frm.add_custom_button(__('Fetch File'), function () {
				frappe.call({
					method: "design.design_management.doctype.drawing_permission.drawing_permission.get_drawing_file",
					args: {
						"item_code": frm.doc.item_code
					},
					callback: function (res) {
						if (res.message) {
							frm.set_value('file_url', res.message)
							frm.set_value('status', 'Ready to Share')
							frm.save()
						}
						else{
							frappe.msgprint('File Not Found')
						}
					}
				})
			});
		}
	},
	to_date: function(frm) {
		if (!frm.doc.from_date){
			frm.set_value('to_date', undefined)
			frappe.msgprint('Enter from date first')
		}
		if (frm.doc.to_date && frm.doc.to_date < frm.doc.from_date){
			frm.set_value('to_date', undefined)
			frappe.msgprint('To Date should be greater than from date')
		}
	}
});
