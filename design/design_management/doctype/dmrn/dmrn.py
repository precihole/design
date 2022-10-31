# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DMRN(Document):
	def on_submit(self):
		self.update_revision_in_item()

	def before_save(self):
		self.custom_validations()

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
			for i in self.dmrn_details:
				revision_c = frappe.db.get_value('Item', i.drawing_no, 'revision_c')
				if revision_c:
					if i.rev_no:
						if i.rev_no == revision_c:
							frappe.throw("Revision is already at "+"<b>"+i.rev_no+"</b>"+" or empty revision")
				else:
					frappe.throw("Revision cannot be empty in Item "+"<b>"+i.drawing_no+"</b>")