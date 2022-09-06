# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignWarehouse(Document):
	pass
	def before_save(self):
		if self.disabled == 1:
			self.status = 'Disabled'
		elif self.disabled == 0:
			self.status = 'Enabled'
