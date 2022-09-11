# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignPrintoutCreation(Document):
	pass
	def on_submit(self):
		#DDN
		if self.stock_entry_type == "Design Transfer" or self.stock_entry_type == "Drawing Discard" or self.stock_entry_type == "Drawing Receipt Confirmation":
			if self.item:
				for i in self.item:
					tar_doc = frappe.db.get_all('Design Bin',filters={'item_code': i.item_code,'warehouse':i.target_warehouse},fields=['name','actual_qty'])
					bin_doc = frappe.db.get_all('Design Bin',filters={'item_code': i.item_code,'warehouse':i.source_warehouse},fields=['name','actual_qty'])
					if tar_doc:
						ledger_minus_entry = frappe.get_doc({
							"doctype":"Design Ledger Entry",
							"item_code":i.item_code,
							"warehouse":i.source_warehouse,
							"posting_date":frappe.utils.nowdate(),
							"posting_time":frappe.utils.nowtime(),
							"voucher_type":"Design Printout Creation",
							"voucher_no":self.name,
							"qty_change":-i.qty,
							"qty_after_transaction":bin_doc[0].actual_qty - i.qty,
							"revision":i.item_code+"-"+i.revision,
							"revision_id":i.revision,
							"revision_no":i.revision
						}).insert(ignore_permissions=True,ignore_mandatory=True)
						ledger_minus_entry.save()
						ledger_plus_entry = frappe.get_doc({
							"doctype":"Design Ledger Entry",
							"item_code":i.item_code,
							"warehouse":i.target_warehouse,
							"posting_date":frappe.utils.nowdate(),
							"posting_time":frappe.utils.nowtime(),
							"voucher_type":"Design Printout Creation",
							"voucher_no":self.name,
							"qty_change":i.qty,
							"qty_after_transaction":tar_doc[0].actual_qty + i.qty,
							"revision":i.item_code+"-"+i.revision,
							"revision_id":i.revision,
							"revision_no":i.revision
						}).insert(ignore_permissions=True,ignore_mandatory=True)
						ledger_plus_entry.save()
					else:
						bin_doc = frappe.db.get_all('Design Bin',filters={'item_code': i.item_code,'warehouse':i.source_warehouse},fields=['name','actual_qty'])
						ledger_minus_entry = frappe.get_doc({
							"doctype":"Design Ledger Entry",
							"item_code":i.item_code,
							"warehouse":i.source_warehouse,
							"posting_date":frappe.utils.nowdate(),
							"posting_time":frappe.utils.nowtime(),
							"voucher_type":"Design Printout Creation",
							"voucher_no":self.name,
							"qty_change":-i.qty,
							"qty_after_transaction":bin_doc[0].actual_qty - i.qty,
							"revision":i.item_code+"-"+i.revision,
							"revision_id":i.revision,
							"revision_no":i.revision
						}).insert(ignore_permissions=True,ignore_mandatory=True)
						ledger_minus_entry.save()
						ledger_entry = frappe.get_doc({
							"doctype":"Design Ledger Entry",
							"item_code":i.item_code,
							"warehouse":i.target_warehouse,
							"posting_date":frappe.utils.nowdate(),
							"posting_time":frappe.utils.nowtime(),
							"voucher_type":"Design Printout Creation",
							"voucher_no":self.name,
							"qty_change":i.qty,
							"qty_after_transaction":i.qty,
							"revision":i.item_code+"-"+i.revision,
							"revision_id":i.revision,
							"revision_no":i.revision
						}).insert(ignore_permissions=True,ignore_mandatory=True)
						ledger_entry.save()
		#DPN Creation
		if self.stock_entry_type == "Drawing Creation":
			if self.item:
				for i in self.item:
					if i.qty > 0:
						bin_doc = frappe.db.get_all('Design Bin',filters={'item_code': i.item_code,'warehouse':i.target_warehouse},fields=['name','actual_qty'])
						if bin_doc:
							ledger_entry = frappe.get_doc({
								"doctype":"Design Ledger Entry",
								"item_code":i.item_code,
								"warehouse":i.target_warehouse,
								"posting_date":frappe.utils.nowdate(),
								"posting_time":frappe.utils.nowtime(),
								"voucher_type":"Design Printout Creation",
								"voucher_no":self.name,
								"qty_change":i.qty,
								"qty_after_transaction":bin_doc[0].actual_qty + i.qty,
								"revision_no":i.revision,
								"revision":i.item_code+"-"+i.revision,
								"revision_id":i.revision
							}).insert(ignore_permissions=True,ignore_mandatory=True)
							ledger_entry.save()
						else:
							ledger_entry = frappe.get_doc({
								"doctype":"Design Ledger Entry",
								"item_code":i.item_code,
								"warehouse":i.target_warehouse,
								"posting_date":frappe.utils.nowdate(),
								"posting_time":frappe.utils.nowtime(),
								"voucher_type":"Design Printout Creation",
								"voucher_no":self.name,
								"qty_change":i.qty,
								"qty_after_transaction":i.qty,
								"revision_no":i.revision,
								"revision":i.item_code+"-"+i.revision,
								"revision_id":i.revision
							}).insert(ignore_permissions=True,ignore_mandatory=True)
							ledger_entry.save()
					elif i.qty == 0:
						frappe.throw("Qty cannot be 0")
		if self.item:
			#check revision qty is available or not in stock
			for o in self.item:
				if o.source_warehouse:
					qty_chk = frappe.db.get_list('Revision Stock Summary',
							filters={
								'item_code': o.item_code,
								'revision':o.revision,
								'warehouse':o.source_warehouse,
								'parent':self.name},
							fields=['actual_qty']
					)
					if qty_chk:
						if o.qty > qty_chk[0].actual_qty:
							frappe.throw(("Quantity not available for "+frappe.bold(o.item_code)+" in warehouse "+frappe.bold(o.source_warehouse)+" for Revision "+frappe.bold(o.revision)
								+ "<br><br>"
								+("Available quantity is "+frappe.bold(qty_chk[0].actual_qty)+", you need "+frappe.bold(float(o.qty)))
								),
									title=("Insufficient Stock"),
							)
					else:
						frappe.throw(("Quantity not available for "+frappe.bold(o.item_code)+" in warehouse "+frappe.bold(o.source_warehouse)+" for Revision "+frappe.bold(o.revision)
							+ "<br><br>"
							+("Available quantity is "+frappe.bold(0)+", you need "+frappe.bold(float(o.qty)))
							),
								title=("Insufficient Stock"),
						)

	def before_save(self):
		if self.item:
			self.set("summary", [])
			for h in self.item:
				revision = frappe.db.get_list('Revision',
						filters={
							'item': h.item_code
						},
						fields=['name'],
						order_by='creation desc',
				)
				for dle in revision:
					ledger_entry = frappe.db.get_list('Design Ledger Entry',
						filters={
							'revision': dle.name,
							'is_cancelled': 0
						},
						fields=['item_code','revision_no','warehouse','sum(qty_change) as qty_change'],
						order_by='creation desc',
						group_by='warehouse'
					)
					for r in ledger_entry:
						if r.qty_change > 0:
							self.append('summary', {
								'item_code' : r.item_code,
								'revision' : r.revision_no,
								'warehouse' : r.warehouse,
								'actual_qty' : r.qty_change    
							})
		# else:
		# 	frappe.msgprint("Item don't have any previous drawing in Stock")
		if 	len(self.get("item")) == 0:
			frappe.throw("Item is Mandatory")
		# if self.stock_entry_type == "Design Transfer" or self.stock_entry_type == "Drawing Discard" or self.stock_entry_type == "Drawing Receipt Confirmation":
		# 	if self.item:
		# 	#check revision qty is available or not in stock
		# 		for o in self.item:
		# 			if o.source_warehouse:
		# 				qty_chk = frappe.db.get_list('Revision Stock Summary',
		# 						filters={
		# 							'item_code': o.item_code,
		# 							'revision':o.revision,
		# 							'warehouse':o.source_warehouse},
		# 						fields=['actual_qty']
		# 				)
		# 				if qty_chk:
		# 					if o.qty > qty_chk[0].actual_qty:
		# 						frappe.throw(("Quantity not available for "+frappe.bold(o.item_code)+" in warehouse "+frappe.bold(o.source_warehouse)+" for Revision "+frappe.bold(o.revision)
		# 							+ "<br><br>"
		# 							+("Available quantity is "+frappe.bold(qty_chk[0].actual_qty)+", you need "+frappe.bold(float(o.qty)))
		# 							),
		# 								title=("Insufficient Stock"),
		# 						)
						# else:
						# 	frappe.throw(("Quantity not available for "+frappe.bold(o.item_code)+" in warehouse "+frappe.bold(o.source_warehouse)+" for Revision "+frappe.bold(o.revision)
						# 		+ "<br><br>"
						# 		+("Available quantity is "+frappe.bold(0)+", you need "+frappe.bold(float(o.qty)))
						# 		),
						# 			title=("Insufficient Stock"),
						# 	)
						if o.source_warehouse == o.target_warehouse:
							frappe.throw("Source and Target Department cannot be same")
	def on_cancel(self):
		for i in self.item:
			lst_doc = frappe.db.get_all('Design Ledger Entry',filters={'voucher_no': self.name,'is_cancelled': 0},fields=['name','item_code','warehouse','qty_change'])
			if lst_doc:
				for j in lst_doc:
					frappe.db.set_value('Design Ledger Entry', j.name, 'is_cancelled', 1)
					bin_update = frappe.db.get_all('Design Bin',filters={'warehouse': j.warehouse,'item_code': j.item_code},fields=['name'])
					actual_qty = frappe.db.get_value('Design Bin', bin_update[0].name, 'actual_qty')
					update_qty = actual_qty - j.qty_change
					frappe.db.set_value('Design Bin', bin_update[0].name, 'actual_qty', update_qty)