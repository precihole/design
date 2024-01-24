# Copyright (c) 2024, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DrawingPermission(Document):
	def before_insert(self):
		if not self.item_code:
			return
		file_url = frappe.db.get_value('File', {'attached_to_doctype': 'Item', 'attached_to_name': self.item_code}, ['file_url'])
		if file_url:
			self.file_url = file_url
			self.status = 'Ready to Share'
		else:
			self.status = 'Draft'
			frappe.msgprint('File Not Found')
	
	def before_save(self):
		if self.item_code and self.file_url:
			if not self.from_date and self.to_date:
				frappe.throw('From date is required')
			elif not self.to_date and self.from_date:
				frappe.throw('To date is required')
				
	def before_submit(self):
		if self.file_url and not self.from_date and not self.to_date:
			self.status = 'Shared'
		elif self.file_url and self.from_date and self.to_date:
			self.status = 'Time-Limited Shared'

@frappe.whitelist()	
def get_drawing_file(item_code):
	file_url = frappe.db.get_value('File', {'attached_to_doctype': 'Item', 'attached_to_name': item_code}, ['file_url'])
	if file_url:
		return file_url