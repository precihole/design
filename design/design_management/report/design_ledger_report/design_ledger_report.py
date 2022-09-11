# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

from cgi import test
from pickletools import read_uint1
import frappe


def execute(filters=None):
	## First, fetch your base data results using normal api calls
	## We can also access `filters`, defined by either the table above or the client script below
	results = frappe.db.get_all('Design Ledger Entry', ['*'],filters=filters,order_by='creation asc')
	design_ledger = [ dic for dic in results if dic.is_cancelled == 0]
	# Then, for fun, let's define a new property programmatically
	qty_change=0
	for result in design_ledger:
		if from_date := filters.get("from_date"):
			j
		if result.qty_change > 0:
			result.in_qty = result.qty_change
		else:
			result.in_qty=0.00
		if result.qty_change < 0:
			result.out_qty = result.qty_change
		else:
			result.out_qty=0.00
		for i in design_ledger:
			if i.revision == result.revision:
				if result.in_qty:
					qty_change = result.in_qty
					break
				elif result.out_qty:
					qty_change = result.out_qty + qty_change
					break
				else:
					qty_change = qty_change + result.qty_change
					break
		result.balance_qty = qty_change
	# dle = frappe.qb.DocType("Design Ledger Entry")
	# query = (
	# 	frappe.qb.from_(dle)
	# 	.select(
	# 		dle.item_code,
	# 		dle.posting_date,
	# 		dle.warehouse,
	# 		dle.posting_time,
	# 		dle.qty_change,
	# 		dle.is_cancelled,
	# 		dle.voucher_type,
	# 		dle.qty_after_transaction,
	# 		dle.voucher_no,
	# 		dle.revision
	# 	)
	# 	.where(
	# 		(dle.docstatus < 2)
	# 		& (dle.is_cancelled == 0)
	# 		& (dle.posting_date[filters.from_date : filters.to_date])
	# 	)
	# 	.orderby(dle.posting_date)
	# 	.orderby(dle.creation)
	# )

	message = "This report has been generated automatically."
	Inventory = [user for user in results if user.warehouse == "Inventory"]
	Design = [user for user in results if user.warehouse == "Design"]

	report_summary = [
		{
			"value": (frappe.utils.nowdate()),
			"label": "Report Date",
			"datatype": "Data",
		},
		{
			"value": len(results),
			"label": "Total users",
			"datatype": "Data",
		}
	]
	## Finally, define your columns. Many of the usual field definition properties are available here for use.
	## If you wanted to, you could also specify these columns in the child table above.
	columns = [
		{
			'fieldname': 'posting_date',
			'label': ('Date'),
			'fieldtype': 'Date',
			'width': 100
		},
		{
			'fieldname': 'item_code',
			'label': ('Item Code'),
			'fieldtype': 'Link',
			'options':"Item",
			'width': 200
		},
		{
			'fieldname': 'in_qty',
			'label': ('In Qty'),
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'fieldname': 'out_qty',
			'label': ('Out Qty'),
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'fieldname': 'balance_qty',
			'label': ('Balance Qty'),
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'fieldname': 'warehouse',
			'label': ('warehouse'),
			'fieldtype': 'Link',
			'options':"Design Warehouse",
			'width': 100
		},
		{
			'fieldname': 'revision',
			'label': ('Revision'),
			'fieldtype': 'Link',
			'options':"Revision",
			'width': 200
		},
		{
			'fieldname': 'voucher_type',
			'label': ('Voucher Type'),
			'fieldtype': 'Link',
			'options':"DocType",
			'width': 200
		},
		{

			'fieldname': 'voucher_no',
			'label': ('Voucher No'),
			'fieldtype': 'Dynamic Link',
			'options':"voucher_type",
			'width': 200
		},
	]

	## finally, we assemble it all together
	data = columns, design_ledger, message, report_summary
	return data