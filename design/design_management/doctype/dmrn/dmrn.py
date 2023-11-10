# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DMRN(Document):
	def before_save(self):
		self.custom_validations()
	
	def before_submit(self):
		for item in self.dmrn_details:
			self.fetch_old_revision(item)

	def on_submit(self):
		self.update_new_revision()
		for item in self.dmrn_details:
			self.link_new_drawing(item)
		
		#delete new drawing from DMRN
		frappe.db.delete("File", {"attached_to_doctype": self.doctype, 'attached_to_name': self.name})
	
	def on_cancel(self):
		self.delete_revision()
		self.update_old_revision()
	
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
	
	def fetch_old_revision(self, item):
		old_revision = frappe.db.get_value('Item', item.item_code, 'revision_c')
		if old_revision:
			item.old_revision = old_revision

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
						"reference_no": self.name,
						"description": "This is automatic entry from DMRN"
					}).insert(ignore_permissions=True,ignore_mandatory=True)
					revision_entry.save()
	
	def link_new_drawing(self, item):
		#delete old drawing
		frappe.db.delete("File", {"attached_to_doctype": 'Item', 'attached_to_name': item.item_code})

		all_drawings = frappe.get_all("File", {'attached_to_doctype': self.doctype, 'attached_to_name': self.name, 'file_url': item.new_drawing}, ['file_name', 'file_url', 'file_size', 'file_type', 'is_private'])
		for drawing in all_drawings:
			link_drawing_to_item = frappe.get_doc({
				"doctype": "File",
				"file_name": drawing.file_name,
				"file_url": drawing.file_url,
				"file_size": drawing.file_size,
				"file_type": drawing.file_type,
				"is_private": drawing.is_private,
				"attached_to_doctype": "Item",
				"attached_to_name": item.item_code
			})
			link_drawing_to_item.insert(ignore_permissions=True,ignore_mandatory=True)

	def delete_revision(self):
		frappe.db.delete("Revision", {"reference_no": self.name})
	
	def update_old_revision(self):
		if self.dmrn_details:
			for item in self.dmrn_details:
				if item.item_code and item.old_revision:
					frappe.db.set_value('Item', item.item_code, 'revision_c', item.old_revision)