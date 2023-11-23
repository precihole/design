# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	results = frappe.db.get_all('Design Ledger Entry', ['*'], filters=filters, order_by='creation asc')
	dl_entries = [ dic for dic in results if dic.is_cancelled == 0]

	qty_change = 0
	for gle in dl_entries:
		if gle.qty_change > 0:
			gle.in_qty = gle.qty_change
		else:
			gle.in_qty = 0.00
		if gle.qty_change < 0:
			gle.out_qty = gle.qty_change
		else:
			gle.out_qty = 0.00
		gle.balance_qty = gle.qty_after_transaction
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

	data = columns, dl_entries, message
	return data