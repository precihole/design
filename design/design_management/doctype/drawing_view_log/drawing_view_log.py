# Copyright (c) 2024, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DrawingViewLog(Document):
	def after_insert(self):
		if self.reference_document == "Drawing Permission":
			views_allowed, current_views = frappe.db.get_value(
				'Drawing Permission Item', 
				self.child_reference_name, 
				['views_allowed', 'views']
			)

			new_views = current_views + 1

			if views_allowed and new_views == views_allowed:
				frappe.db.set_value('Drawing Permission Item', self.child_reference_name, 'views', new_views)
				frappe.db.set_value('Drawing Permission', self.reference_name, 'status', 'Expired')
			elif not views_allowed or new_views < views_allowed:
				frappe.db.set_value('Drawing Permission Item', self.child_reference_name, 'views', new_views)
