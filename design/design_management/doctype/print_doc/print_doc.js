// Copyright (c) 2022, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Print Doc', {
	refresh: function(frm) {
		var printerList=[];
		frappe.call({
			async:false,
			method:'design.design_management.doctype.print_doc.print_doc.get_printer_list',
			callback:function(res){
				if(res.message !== undefined){
					console
					var responseData = res.message.data
					const defaultPrinter = responseData[0]
					const systemPrinter = defaultPrinter.split(" ").pop()
					for(var i=1;i<responseData.length;i++){
						printerList.push(responseData[i].split(/\s(.+)/)[0])
					}
					//console.log(printerList)default_printer
					frm.set_df_property('printer_list', 'options', printerList);
					frm.set_value('default',systemPrinter)
					frm.refresh_field("printer_list","default_printer");
				}
			}
		})
	}
});
