// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt
frappe.ui.form.on('DMRN', {
	refresh: function(frm) {
		if(frm.doc.__islocal){
			frm.clear_table("dmrn_details");
			frm.add_child("dmrn_details");
			frm.refresh_fields("dmrn_details");

			if(!frm.doc.originator){
				frm.set_value('originator', frappe.session.user);
			}   
		}

		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__("Create Design Distribution"), function() {
				frappe.route_options = {
					'reference_no': frm.doc.name,
					'entry_type': 'Drawing Transfer'
				};
				frappe.set_route('Form','Design Distribution',"new-design-distribution-wicrykkhju");
			});
		}

		if(frm.doc.__islocal && frm.doc.reference_no){
			frappe.call({
				async: false,
				method: "frappe.client.get",
				args: {
					"doctype": "ECN",
					"filters": {
						'name': frm.doc.reference_no
					},
					"fieldname": ['item_code', 'revision']
				},
				callback: function (res) {
					if (res.message && res.message.revision !== undefined) {
						var revision_prefix = res.message.revision.charAt(0);
						var revision_no = parseInt(res.message.revision.slice(1));
						revision_no += 1;
						var new_revision = revision_prefix + revision_no;
		
						frm.clear_table("dmrn_details");
						var addDMRNDetail = frm.add_child("dmrn_details");
						addDMRNDetail.item_code = res.message.item_code;
						addDMRNDetail.new_revision = new_revision;
						frm.refresh_fields("dmrn_details");
					} else {
						// Handle the case where res.message or res.message.revision is null or undefined.
						console.error("The response does not contain the expected data.");
					}
				}
			})
		}		
	}
});
