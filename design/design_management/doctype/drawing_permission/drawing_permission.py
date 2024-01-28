# Copyright (c) 2024, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DrawingPermission(Document):
	def before_save(self):
		if not self.item_code:
			return
		file_urls = frappe.db.get_all('File', {'attached_to_doctype': 'Item', 'attached_to_name': self.item_code}, ['file_url'])
		if not file_urls:
			self.files = []
			frappe.msgprint('File Not Found')
		existing_file_urls = [row.file_url for row in self.files]
		for file in file_urls:
			if file.file_url not in existing_file_urls:
				row = self.append('files', {})
				row.child_item_code = self.item_code
				row.file_url = file.file_url
				
	def before_submit(self):
		self.status = 'Shared'

@frappe.whitelist()
def get_item_drawing_file_urls(item_code):
    return frappe.db.get_all('File', {'attached_to_doctype': 'Item', 'attached_to_name': item_code}, ['file_url']) or None
	
@frappe.whitelist()
def log_view_if_not_expired(reference_name):
	DP = frappe.db.get_value('Drawing Permission Item', reference_name, 'parent')
	status = frappe.db.get_value('Drawing Permission', DP, 'status')
	if status != 'Expired':
		doc = frappe.get_doc({
            "doctype": "Drawing View Log",
			"viewed_by": frappe.session.user,
			"reference_document": "Drawing Permission",
			"reference_name": DP,
			"child_reference_name": reference_name
        	}).insert(ignore_permissions=True,ignore_mandatory=True)
		doc.save()