// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('DMRN', {
	refresh: function(frm) {
		if(frm.doc.__islocal){
			if(frm.doc.originator === undefined){
				cur_frm.set_value('originator', frappe.session.user);
			}   
		}		
	}
});
