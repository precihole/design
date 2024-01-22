# Copyright (c) 2024, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DrawingPermission(Document):
	def before_save(self):
		self.file_url = frappe.utils.get_url() + self.file_url
