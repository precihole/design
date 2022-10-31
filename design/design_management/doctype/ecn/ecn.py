# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ECN(Document):
	def before_save(self):
		#self.clear_child()
		self.add_warehouse_details()

	def clear_child(self):
		if self.warehouse_detail:
			self.set("warehouse_detail", [])

	def add_warehouse_details(self):
		if self.item_code:
			bin_list = frappe.db.get_list('Bin',filters={'item_code': self.item_code},fields=['item_code','warehouse', 'actual_qty'])
			total_qty = 0
			if bin_list:
				for i in bin_list:
					total_qty = total_qty + i.actual_qty
				if total_qty > 0:
					self.clear_child()
					for j in bin_list:
						if j.actual_qty > 0:
							self.append('warehouse_detail', {
								'item_code' : j.item_code,
								'warehouse' : j.warehouse,
								'actual_qty' : j.actual_qty  
							})
					self.total_qty = total_qty
				elif total_qty == 0:
					self.clear_child()
					self.total_qty = 0
			else:
				self.clear_child()
				self.total_qty = 0