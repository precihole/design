# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DMRN(Document):
	def before_save(self):
		self.custom_validations()

	def on_submit(self):
		self.update_new_revision()
	
	def on_cancel(self):
		self.delete_revision()
	
	def custom_validations(self):
		if self.dmrn_details:
			for item in self.dmrn_details:
				old_revision = frappe.db.get_value('Item', item.item_code, 'revision_c')
				if old_revision:
					if item.new_revision:
						if item.new_revision == old_revision:
							frappe.throw(f"Revision is already at {item.new_revision} in <b>{item.item_code}</b>")
					else:
						frappe.throw(f"New revision cannot be empty in <b>{item.item_code}</b>")
				else:
					frappe.throw(f"Revision is empty in Item Master <b>{item.item_code}</b>")

	def update_new_revision(self):
		if self.dmrn_details:
			for item in self.dmrn_details:
				if item.item_code and item.new_revision:
					doc = frappe.get_doc("Item", item.item_code)
					doc.revision_c = item.new_revision
					doc.save()
					revision_entry = frappe.get_doc({
						"doctype": "Revision",
						"revision": item.new_revision,
						"item_code": item.item_code,
						"reference_no": self.name
					}).insert(ignore_permissions=True,ignore_mandatory=True)
					revision_entry.save()

	def delete_revision(self):
		frappe.db.delete("Revision", {"reference_no": self.name})