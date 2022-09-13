# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DesignPrintoutCreation(Document):
	def before_insert(self):
		self.set_series()

	def before_save(self):
		self.set_series() #series
		self.custom_validation() #all validations
		self.item_stock_summary() #summary

	def before_submit(self):
		self.status_update()

	def on_submit(self):
		#only dle in created on submit
		#Note:Bin Entry created on insert of dle
		self.create_dle_entry()

	def on_cancel(self):
		self.cancel_dle_entry()
						
	def set_series(self):
		if self.stock_entry_type == 'Drawing Creation':
			self.naming_series = 'DT-CN-.YYYY.-'
		elif self.stock_entry_type == 'Drawing Transfer':
			self.naming_series = 'DT-.YYYY.-'
		elif self.stock_entry_type == 'Drawing Receipt':
			self.naming_series = 'DT-REC-.YYYY.-'
		elif self.stock_entry_type == 'Drawing Return':
			self.naming_series = 'DT-RT-.YYYY.-'
		elif self.stock_entry_type == 'Drawing Discard':
			self.naming_series = 'DT-DC-.YYYY.'

	def custom_validation(self):
		if self.item:
			for o in self.item:
				#warehouse validate
				if o.source_warehouse == o.target_warehouse:
					frappe.throw("Source and target warehouse cannot be same for row "+str(o.idx))
				
				#qty 0 validate
				if o.qty == 0:
					frappe.throw("Row "+(str(o.idx)+": Qty is mandatory"
						),
							title=("Zero quantity"),
					)
				
				#in stock qty validate
				if self.stock_entry_type == ('Drawing Transfer' or 'Drawing Return' or 'Drawing Discard' or 'Drawing Receipt'):
					if o.source_warehouse:
						qty_chk = frappe.db.get_all('Revision Stock Summary',
								filters={
									'item_code': o.item_code,
									'revision':o.revision,
									'warehouse':o.source_warehouse},
								fields=['actual_qty']
						)
						if qty_chk:
							if o.qty > qty_chk[0].actual_qty:
								frappe.throw(("Quantity not available for "
									+frappe.bold(o.item_code)
									+" in warehouse "+frappe.bold(o.source_warehouse)
									+" for Revision "+frappe.bold(o.revision)
									+ "<br><br>"
									+("Available quantity is "+frappe.bold(qty_chk[0].actual_qty)
									+", you need "+frappe.bold(float(o.qty)))
									),
										title=("Insufficient Stock"),
								)
						else:
							#if not islocal
							if not self.is_new():
								frappe.throw(("Quantity not available for "
									+frappe.bold(o.item_code)
									+" in warehouse "+frappe.bold(o.source_warehouse)
									+" for Revision "+frappe.bold(o.revision)
									+ "<br><br>"
									+("Available quantity is "+frappe.bold(0)
									+", you need "+frappe.bold(float(o.qty)))
									),
										title=("Insufficient Stock"),
								)
	def item_stock_summary(self):
		unique_list = []
		if self.item:
			for i in self.item:
				if i.item_code not in unique_list:
					#unique item code list for ledger summary
					unique_list.append(i.item_code)
			#set summary item table to empty
			self.set("summary", [])
			for h in unique_list:
				#fetch all revision of item code
				revision = frappe.db.get_list('Revision',
						filters={
							'item': h
						},
						fields=['name'],
						order_by='creation desc',
				)
				for dle in revision:
					#fetch dle of each revision
					ledger_entry = frappe.db.get_list('Design Ledger Entry',
						filters={
							'revision': dle.name,
							'is_cancelled': 0
						},
						fields=['item_code','revision_no','warehouse','sum(qty_change) as qty_change'],
						order_by='creation desc',
						group_by='warehouse'
					)
					if ledger_entry:
						for r in ledger_entry:
							if r.qty_change > 0:
								self.append('summary', {
									'item_code' : r.item_code,
									'revision' : r.revision_no,
									'warehouse' : r.warehouse,
									'actual_qty' : r.qty_change    
								})
	def status_update(self):
		self.status = 'To Receive and Return'

	def create_dle_entry(self):
		if self.item:
			for i in self.item:
				source_ware_bin = frappe.db.get_all('Design Bin',
						filters={
							'item_code': i.item_code,
							'warehouse':i.source_warehouse
						},
						fields=['name','actual_qty'])
				target_ware_bin = frappe.db.get_all('Design Bin',
						filters={
							'item_code': i.item_code,
							'warehouse':i.target_warehouse
						},
						fields=['name','actual_qty'])
				if self.stock_entry_type == ('Drawing Transfer' or 'Drawing Return' or 'Drawing Discard' or 'Drawing Receipt'):
					#two cases for dle
					#1. If Target Bin already then already_qty + current_qty
					#2. If Target Bin not available then current_qty
					if source_ware_bin and target_ware_bin:
						self.dle_entry(i,source_ware_bin,target_ware_bin)
					elif source_ware_bin:
						self.dle_entry(i,source_ware_bin,None)
				elif self.stock_entry_type == "Drawing Creation":
					if i.qty > 0:
						if target_ware_bin:
							self.dle_entry(i,None,target_ware_bin)
						else:
							self.dle_entry(i,None,None)
					#just for backup Cos validation on ui is already there
					elif i.qty == 0:
						frappe.throw("Qty cannot be 0")
	
	def dle_entry(self,i,source_ware_bin,target_ware_bin):
		if not source_ware_bin == None:
			minus_dle_entry = frappe.get_doc({
				"doctype":"Design Ledger Entry",
				"item_code":i.item_code,
				"warehouse":i.source_warehouse,
				"posting_date":frappe.utils.nowdate(),
				"posting_time":frappe.utils.nowtime(),
				"voucher_type":"Design Printout Creation",
				"voucher_no":self.name,
				"qty_change":-i.qty,
				"qty_after_transaction":source_ware_bin[0].actual_qty - i.qty,
				"revision":i.item_code+"-"+i.revision,
				"revision_id":i.revision,
				"revision_no":i.revision
			}).insert(ignore_permissions=True,ignore_mandatory=True)
			minus_dle_entry.save()
		if target_ware_bin == None:
			plus_dle_entry = frappe.get_doc({
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
			plus_dle_entry.save()
		else:
			plus_dle_entry = frappe.get_doc({
				"doctype":"Design Ledger Entry",
				"item_code":i.item_code,
				"warehouse":i.target_warehouse,
				"posting_date":frappe.utils.nowdate(),
				"posting_time":frappe.utils.nowtime(),
				"voucher_type":"Design Printout Creation",
				"voucher_no":self.name,
				"qty_change":i.qty, #qty to be plus
				"qty_after_transaction":target_ware_bin[0].actual_qty + i.qty, #plus qty in target
				"revision":i.item_code+"-"+i.revision,
				"revision_id":i.revision,
				"revision_no":i.revision
			}).insert(ignore_permissions=True,ignore_mandatory=True)
			plus_dle_entry.save()

	def cancel_dle_entry(self):
		for i in self.item:
			lst_doc = frappe.db.get_all('Design Ledger Entry',
				filters={
					'voucher_no': self.name,
					'is_cancelled': 0
				},
				fields=['name','item_code','warehouse','qty_change'])
			if lst_doc:
				for j in lst_doc:
					frappe.db.set_value('Design Ledger Entry', j.name, 'is_cancelled', 1)
					bin_update = frappe.db.get_all('Design Bin',
						filters={
							'warehouse': j.warehouse,
							'item_code': j.item_code
						},
						fields=['name'])
					actual_qty = frappe.db.get_value('Design Bin', bin_update[0].name, 'actual_qty')
					update_qty = actual_qty - j.qty_change
					frappe.db.set_value('Design Bin', bin_update[0].name, 'actual_qty', update_qty)