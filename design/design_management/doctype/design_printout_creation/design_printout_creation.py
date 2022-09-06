# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignPrintoutCreation(Document):
	pass
	def on_submit(self):
		if self.item:
			for i in self.item:
				if i.qty > 0:
					bin_doc = frappe.db.get_all('Design Bin',filters={'item_code': i.item_code,'warehouse':i.target_warehouse},fields=['name','actual_qty'])
					if bin_doc:
						ledger_entry = frappe.get_doc({
							"doctype":"Design Ledger Entry",
							"item_code":i.item_code,
							"warehouse":i.target_warehouse,
							"posting_date":frappe.utils.nowdate(),
							"posting_time":frappe.utils.nowtime(),
							"voucher_type":"Design Printout Creation",
							"voucher_no":self.name,
							"qty_change":i.qty,
							"qty_after_transaction":bin_doc[0].actual_qty + i.qty,
							"revision_no":i.revision
						}).insert(ignore_permissions=True,ignore_mandatory=True)
						ledger_entry.save()
					else:
						ledger_entry = frappe.get_doc({
							"doctype":"Design Ledger Entry",
							"item_code":i.item_code,
							"warehouse":i.target_warehouse,
							"posting_date":frappe.utils.nowdate(),
							"posting_time":frappe.utils.nowtime(),
							"voucher_type":"Design Printout Creation",
							"voucher_no":self.name,
							"qty_change":i.qty,
							"qty_after_transaction":i.qty,
							"revision_no":i.revision
						}).insert(ignore_permissions=True,ignore_mandatory=True)
						ledger_entry.save()
				elif i.qty == 0:
					frappe.throw("Qty cannot be 0")
	def on_cancel(self):
		for i in self.item:
			lst_doc = frappe.db.get_all('Design Ledger Entry',filters={'voucher_no': self.name,'is_cancelled': 0},fields=['name','item_code','warehouse','qty_change'])
			if lst_doc:
				for j in lst_doc:
					frappe.db.set_value('Design Ledger Entry', j.name, 'is_cancelled', 1)
					bin_update = frappe.db.get_all('Design Bin',filters={'warehouse': j.warehouse,'item_code': j.item_code},fields=['name'])
					actual_qty = frappe.db.get_value('Design Bin', bin_update[0].name, 'actual_qty')
					update_qty = actual_qty - j.qty_change
					frappe.db.set_value('Design Bin', bin_update[0].name, 'actual_qty', update_qty)