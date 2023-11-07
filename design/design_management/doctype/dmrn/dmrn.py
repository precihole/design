# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DMRN(Document):
	def before_save(self):
		self.custom_validations()

	def on_submit(self):
		self.update_revision_in_item()

	def update_revision_in_item(self):
		if self.dmrn_details:
			for i in self.dmrn_details:
				if i.drawing_no:
					item_doc = frappe.get_doc("Item",  i.drawing_no)
					item_doc.revision_c = i.rev_no
					item_doc.save()
				if i.rev_no:
					revision_entry = frappe.get_doc({
					"doctype":"Revision",
					"revision_id":i.rev_no,
					"item":i.drawing_no,
					"reference_no":self.name
					}).insert(ignore_permissions=True,ignore_mandatory=True)
					revision_entry.save()
	
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