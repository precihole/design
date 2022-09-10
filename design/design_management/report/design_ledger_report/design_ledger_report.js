// Copyright (c) 2022, Rehan Ansari and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Design Ledger Report"] = {
	"filters": [
		{
			'fieldname': 'from_date',
			'label': ('From Date'),
			'fieldtype': 'Date',
			'width': 300
		},
		{
			'fieldname': 'to_date',
			'label': ('To Date'),
			'fieldtype': 'Date',
			'width': 300
		},
		{
			'fieldname': 'item_code',
			'label': ('Item Code'),
			'fieldtype': 'Link',
			'options':"Item",
			'width': 200
		},
		{
			'fieldname': 'warehouse',
			'label': ('Warehouse'),
			'fieldtype': 'Link',
			'options':"Design Warehouse",
			'width': 200
		},
		{
			'fieldname': 'revision',
			'label': ('Revision'),
			'fieldtype': 'Link',
			'options':"Revision",
			'width': 200
		},
		{

			'fieldname': 'voucher_no',
			'label': ('Voucher No'),
			'fieldtype': 'Data',
			'width': 200
		},
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);	
		if (column.id == "in_qty") {
			if (data["in_qty"] > 0) {
				// value = `<span class='text-success'>${data['in_qty']}</span>`;
				value = "<span style='color:green;'>" + data['in_qty'] + "</span>";
			} 
		}
		if (column.id == "out_qty") {
			if (data["out_qty"] < 0) {
				value = "<span style='color:red;'>" + data['out_qty'] + "</span>";
		
			}
		}	
		return value
	}
	
};
