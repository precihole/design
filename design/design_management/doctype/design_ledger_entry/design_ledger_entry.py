# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignLedgerEntry(Document):
	def after_insert(self):
		bin_entry = frappe.db.get_value('Design Bin', {'item_code': self.item_code, 'warehouse': self.warehouse})
		if bin_entry:
			# Update existing Design Bin entry
			frappe.db.set_value('Design Bin', bin_entry, 'actual_qty', self.qty_after_transaction)
		else:
			# Create a new Design Bin entry
			new_bin_entry = frappe.get_doc({
				"doctype": "Design Bin",
				"item_code": self.item_code,
				"warehouse": self.warehouse,
				"actual_qty": self.qty_after_transaction
				})
			new_bin_entry.insert(ignore_permissions=True, ignore_mandatory=True)
			new_bin_entry.save()
