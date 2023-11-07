# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ECN(Document):
	def before_save(self):
		#self.clear_child()
		self.add_warehouse_details()

	def add_warehouse_details(self):
		if self.item_code:
			bin_list = frappe.db.get_all('Bin', {'item_code': self.item_code}, ['item_code','warehouse', 'actual_qty'])
			total_qty = 0
			if bin_list:
				for item in bin_list:
					total_qty = total_qty + item.actual_qty
				if total_qty > 0:
					self.clear_child()
					for item in bin_list:
						if item.actual_qty > 0:
							self.append('warehouse_details', {
								'item_code' : item.item_code,
								'warehouse' : item.warehouse,
								'actual_qty' : item.actual_qty  
							})
					self.total_qty = total_qty
				elif total_qty == 0:
					self.clear_child()
					self.total_qty = 0
			else:
				self.clear_child()
				self.total_qty = 0
	
	def clear_child(self):
		if self.warehouse_details:
			self.set("warehouse_details", [])