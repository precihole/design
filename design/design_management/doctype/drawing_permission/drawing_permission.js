// Copyright (c) 2024, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Drawing Permission', {
	refresh: function(frm) {
		if (frm.doc.item_code && frm.doc.docstatus == 0){
			frm.add_custom_button(__('Fetch File'), function () {
				frappe.call({
					method: "design.design_management.doctype.drawing_permission.drawing_permission.get_item_drawing_file_urls",
					args: {
						"item_code": frm.doc.item_code
					},
					callback: function (res) {
						if (res.message) {
							let fileData = res.message;
							frm.set_value('files', [])
							fileData.forEach(data => {
								let child_row = frm.add_child('files');
								child_row.child_item_code = frm.doc.item_code
								child_row.file_url = data.file_url
							});
							frm.refresh_field('files');
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
	item_code: function(frm) {
		if (frm.doc.item_code){
			frm.set_value('files', [])
			frm.refresh_field('files');
		}
	},
	// to_date: function(frm) {
	// 	if (!frm.doc.from_date){
	// 		frm.set_value('to_date', undefined)
	// 		frappe.msgprint('Enter from date first')
	// 	}
	// 	if (frm.doc.to_date && frm.doc.to_date < frm.doc.from_date){
	// 		frm.set_value('to_date', undefined)
	// 		frappe.msgprint('To Date should be greater than from date')
	// 	}
	// }
});
