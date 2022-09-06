# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignLedgerEntry(Document):
	pass
	def after_insert(self):
		if self.voucher_type == "DDN":
			if self.qty_change < 0:
				bin_doc = frappe.db.get_all('Design Bin',filters={'warehouse':self.warehouse,'item_code': self.item_code},fields=['name','actual_qty'])
				if bin_doc:
					temp = bin_doc[0].actual_qty + self.qty_change
					frappe.db.set_value('Design Bin', bin_doc[0].name, 'actual_qty', temp)
				else:
					frappe.throw("Bin Warehouse not available")
			else:
				bin_doc = frappe.db.get_all('Design Bin',filters={'warehouse':self.warehouse,'item_code': self.item_code},fields=['name'])
				if bin_doc:
					frappe.db.set_value('Design Bin', bin_doc[0].name, 'actual_qty', self.qty_after_transaction)
				else:
					bin_entry = frappe.get_doc({
						"doctype":"Design Bin",
						"warehouse":self.warehouse,
						"item_code":self.item_code,	
						"actual_qty":self.qty_after_transaction
					}).insert(ignore_permissions=True,ignore_mandatory=True)
					bin_entry.save()
		elif self.voucher_type == "Design Printout Creation":
			bin_doc = frappe.db.get_all('Design Bin',filters={'warehouse':self.warehouse,'item_code': self.item_code},fields=['name'])
			if bin_doc:
				frappe.db.set_value('Design Bin', bin_doc[0].name, 'actual_qty', self.qty_after_transaction)
			else:
				bin_entry = frappe.get_doc({
					"doctype":"Design Bin",
					"warehouse":self.warehouse,
					"item_code":self.item_code,
					"actual_qty":self.qty_after_transaction
				}).insert(ignore_permissions=True,ignore_mandatory=True)
				bin_entry.save()