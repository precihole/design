// Copyright (c) 2023, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Print Settings', {
	refresh: function(frm) {
		var printerList=[];
		frappe.call({
			async:false,
			method:'design.design_management.doctype.design_print_settings.design_print_settings.get_printer_list',
			callback:function(res){
				if(res.message !== undefined){
					var responsePrinterList = res.message.data
					const defaultPrinter = responsePrinterList[0]
					const systemPrinter = defaultPrinter.split(" ").pop()
					for(var printer = 1; printer < responsePrinterList.length; printer++){
						printerList.push(responseData[printer].split(/\s(.+)/)[0])
					}
					frm.set_df_property('printer_list', 'options', printerList)
					frm.set_value('default', systemPrinter)
					frm.refresh_field("printer_list", "default_printer")
				}
			}
		})
	},
	check_status: function(frm) {
		frappe.call({
			method:'design.design_management.doctype.design_print_settings.design_print_settings.get_printer_status',
			callback:function(res){
				if(res.message !== undefined){
					console.log(res.message)
				}
			}
		})
	}
});
