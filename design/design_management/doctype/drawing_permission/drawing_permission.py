# Copyright (c) 2024, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DrawingPermission(Document):
	def before_insert(self):
		self.status = 'Draft'

	def before_save(self): #exceptional case
		if not self.item_code:
			return
		if not self.files: #clash with client side call
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
					row.child_status = 'Draft'
		for item in self.files:
			if item.view_based_sharing == 1 and item.views_allowed == 0:
				frappe.throw('View is req')
			elif item.date_based_sharing == 1 and not item.from_date and not item.to_date:
				frappe.throw('Date is req')

	def before_submit(self):
		if not self.attached_to_name:
			frappe.throw('Supplier Name req	')
		self.status = 'Shared'
		for item in self.files:
			item.child_status = 'Shared'
	
	def before_cancel(self):
		self.status = 'Cancelled'
		for item in self.files:
			item.child_status = 'Cancelled'

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

def auto_expired():
	shared_list = frappe.db.get_all('Drawing Permission Item', {'status': 'Shared', 'to_date': ['<', frappe.utils.nowdate()]}, pluck='name')
	if shared_list:
		frappe.db.set_value('Drawing Permission Item', shared_list, 'child_status', 'Expired')