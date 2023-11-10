// Copyright (c) 2023, Precihole and contributors
// For license information, please see license.txt

frappe.ui.form.on('Design Print Settings', {
	refresh: function(frm) {
		function setStyle(element, styleObj) {
			for (const style in styleObj) {
				element.style[style] = styleObj[style];
			}
		}
		function setColour(value) {
			const fieldElements = document.querySelectorAll(`[data-fieldname=${value}]`);
			const styleObj = {
				backgroundColor: '#2490ef',
				color: '#fff',
				paddingTop: '7px',
				paddingBottom: '7px',
				paddingLeft: '10px',
				paddingRight: '10px',
				height: '30px',
				width: '130px',
				marginTop: '27px',
			};
			setStyle(fieldElements[1], styleObj);
		}
		setColour("set_default");
		setColour("check_status");

		frappe.call({
			async: false,
			method: 'design.design_management.doctype.design_print_settings.design_print_settings.fetch_printer_information',
			callback: function (response) {
				if (response.message !== undefined) {
					const responsePrinterList = response.message.data;
					const defaultPrinter = responsePrinterList[0].split(" ").pop();
					const additionalPrinters = responsePrinterList.slice(1).map(function (printer) {
						return printer.split(/\s(.+)/)[0];
					});

					frm.set_df_property('printer_list', 'options', additionalPrinters);
					frm.refresh_field("printer_list", "default_printer");

					frm.set_value('default', defaultPrinter);
				}
			}
		});

	},
	set_default: function(frm) {
		if(frm.doc.printer_list && frm.doc.printer_list !== frm.doc.default){
			frappe.call({
				method: 'design.design_management.doctype.design_print_settings.design_print_settings.set_default_printer',
				args: {
					printer_name: frm.doc.printer_list
				},
				callback: function(res) {
					if (res.message !== undefined) {
						console.log(res.message);
					}
				}
			});
		}
		else if (frm.doc.printer_list == frm.doc.default){
			frappe.msgprint('The selected printer is already set as the default printer.')
		}
		else if(!frm.doc.printer_list){
			frappe.msgprint("Please select a printer before setting it as the default.");
		}
	},
	check_status: function(frm) {
		if(frm.doc.ip_address){
			frappe.call({
				method:'design.design_management.doctype.design_print_settings.design_print_settings.check_printer_status',
				args: {
					ip_address: frm.doc.ip_address
				},
				callback:function(res){
					if(res.message !== undefined){
						console.log(res.message)
					}
				}
			})
		}
		else{
			frappe.msgprint('Please provide an IP address to check the printer status.')
		}
	}
});
