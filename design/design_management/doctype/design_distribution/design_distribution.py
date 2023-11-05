# Copyright (c) 2023, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignDistribution(Document):
	def on_submit(self):
		if self.items:
			for item in self.items:
				if self.entry_type == 'Drawing Transfer':
					# Produce design quantities
					self.produceDesignQuantities(item)
					
					# Transfer to transit
					self.transferToTransit(item)

	def produceDesignQuantities(self, item):
		if item.qty > 0:
			self.create_dle_entry(item, item.s_warehouse, None, 1)

	def transferToTransit(self, item):
		# Step 1: Subtract from source warehouse
		self.create_dle_entry(item, item.s_warehouse, None, 0)

		# Step 2: Add to Transit
		self.create_dle_entry(item, None, 'Transit', 1)

	def create_dle_entry(self, item, source, target, flag):
		# Calculate the result based on flag and actual_qty
		actual_qty = frappe.db.get_value('Design Bin', {'item_code': item.item_code, 'warehouse': target if source is None else source}, ['actual_qty'])
		result = item.qty + actual_qty if flag == 1 and actual_qty else item.qty - actual_qty if actual_qty else item.qty

		# Create a new Design Ledger Entry
		new_dle_entry = frappe.get_doc({
			"doctype": "Design Ledger Entry",
			"item_code": item.item_code,
			"warehouse": target if source is None else source,
			"posting_date": frappe.utils.nowdate(),
			"posting_time": frappe.utils.nowtime(),
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"qty_change": item.qty if flag == 1 else -item.qty,
			"qty_after_transaction": result
		})

		# Insert and save the new Design Ledger Entry
		new_dle_entry.insert(ignore_permissions=True, ignore_mandatory=True)
		new_dle_entry.save()

@frappe.whitelist()	
def ping():
	return 'pong'

@frappe.whitelist()
def update_received_qty():
	received_qty = frappe.db.get_value('Design Distribution Item', frappe.form_dict.id, 'received_qty')
	if received_qty:
		frappe.db.set_value('Design Distribution Item', frappe.form_dict.id, 'received_qty', frappe.utils.flt(frappe.form_dict.qty) + frappe.utils.flt(received_qty))
	else:
		frappe.db.set_value('Design Distribution Item', frappe.form_dict.id, 'received_qty', frappe.utils.flt(frappe.form_dict.qty))
	return True

@frappe.whitelist()
def create_dle_entry(self, item, source, target, flag):
	# Calculate the result based on flag and actual_qty
	actual_qty = frappe.db.get_value('Design Bin', {'item_code': item.item_code, 'warehouse': target if source is None else source}, ['actual_qty'])
	result = item.qty + actual_qty if flag == 1 and actual_qty else item.qty - actual_qty if actual_qty else item.qty

	# Create a new Design Ledger Entry
	new_dle_entry = frappe.get_doc({
		"doctype": "Design Ledger Entry",
		"item_code": item.item_code,
		"warehouse": target if source is None else source,
		"posting_date": frappe.utils.nowdate(),
		"posting_time": frappe.utils.nowtime(),
		"voucher_type": self.doctype,
		"voucher_no": self.name,
		"qty_change": item.qty if flag == 1 else -item.qty,
		"qty_after_transaction": result
	})

	# Insert and save the new Design Ledger Entry
	new_dle_entry.insert(ignore_permissions=True, ignore_mandatory=True)
	new_dle_entry.save()