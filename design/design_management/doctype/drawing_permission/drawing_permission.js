// Copyright (c) 2024, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Drawing Permission', {
	refresh: function(frm) {
		frm.set_intro("🔗Shared", "red")
		$('.grid-add-row').hide()
		if (frm.doc.item_code && frm.doc.docstatus == 0) {
			//remove (!frm.doc.files || frm.doc.files.length === 0) condition
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
							$('.grid-add-row').hide()
						}
						else{
							frappe.msgprint({
								title: __('File Not Found'),
								message: __(`No files available for item code <b>${frm.doc.item_code}</b>. Please verify the code or upload files.`),
								indicator: 'orange'
							});
						}
					}
				})
			});
		}
	},
	item_code: function(frm) {
		if (frm.doc.item_code){
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
						$('.grid-add-row').hide()
					}
					else{
						frm.set_value('files', [])
						frappe.msgprint({
							title: __('File Not Found'),
							message: __(`No files available for item code <b>${frm.doc.item_code}</b>. Please verify the code or upload files.`),
							indicator: 'orange'
						});
					}
				}
			})
		}
	},
	onload: function(frm) {
        var css = `
			div[data-fieldname="child_status"]:not([title="Status"]) .static-area.ellipsis {
				background: var(--bg-purple);color: var(--text-on-purple);
				padding: 3px 10px;
				border-radius: 13px;
				display: inline-block;
				text-align: center;
				font-size: 12px;
				line-height: 1.5;
				vertical-align: middle;
			}
        `;
        $("<style>").prop("type", "text/css").html(css).appendTo("head");
    }
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
frappe.ui.form.on('Drawing Permission Item', {
	files_remove: function(frm) {
		setTimeout(function() {
			$('.grid-add-row').hide();
		}, 100); // 1000 milliseconds = 1 second
	},
	form_render: function(frm) {
		$('.grid-insert-row-below').hide(); // Hides the "Insert Below" button
		$('.grid-insert-row').hide(); // Hides the "Insert Above" button
		$('.grid-duplicate-row').hide(); // Hides the "Duplicate" button
	},
	file_display: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		let baseUrl = window.location.origin;
		window.location.href = `${baseUrl}${d.file_url}`
	}
})