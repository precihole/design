# Copyright (c) 2023, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import subprocess, sys
import tempfile
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import lightgrey
import json

class DesignDistribution(Document):
	def before_save(self):
		if self.entry_type == 'Drawing Transfer':
			self.item_stock_summary()
	
	def before_submit(self):
		self.set_status()

	def on_submit(self):
		if self.items:
			for item in self.items:
				if self.entry_type == 'Drawing Transfer':
					# Produce design quantities
					self.produceDesignQuantities(item)

					# Transfer to Target
					self.transferQuantities(item)
					self.print_design_drawings_per_item(item)
				elif self.entry_type == "Drawing Return":
					# Transfer to Target
					self.transferQuantities(item)
				elif self.entry_type == "Drawing Discard":
					self.discardDesignQuantities(item)
				
	def on_cancel(self):
		self.cancel_dle_entry()

	def produceDesignQuantities(self, item):
		if item.qty > 0:
			self.create_dle_entry(item, item.s_warehouse, None, 1)

	def transferQuantities(self, item):
		# Step 1: Subtract from source warehouse
		self.create_dle_entry(item, item.s_warehouse, None, 0)

		# Step 2: Add to Target
		self.create_dle_entry(item, None, item.t_warehouse, 1)
	
	def discardDesignQuantities(self, item):
		self.create_dle_entry(item, item.s_warehouse, None, 0)

	def create_dle_entry(self, item, source, target, flag):
		# Calculate the result based on flag and actual_qty
		actual_qty = frappe.db.get_value('Design Bin', {'item_code': item.item_code, 'warehouse': target if source is None else source}, ['actual_qty'])
		result = item.qty + actual_qty if flag == 1 and actual_qty else actual_qty - item.qty if actual_qty else item.qty

		# Create a new Design Ledger Entry
		new_dle_entry = frappe.get_doc({
			"doctype": "Design Ledger Entry",
			"item_code": item.item_code,
			"warehouse": target if source is None else source,
			"posting_date": frappe.utils.nowdate(),
			"posting_time": frappe.utils.nowtime(),
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"qty_change": item.qty if flag == 1 else -item.qty,
			"qty_after_transaction": result,
			"revision": item.item_code+"-"+item.revision,
			"revision_no": item.revision
		})

		# Insert and save the new Design Ledger Entry
		new_dle_entry.insert(ignore_permissions=True, ignore_mandatory=True)
		new_dle_entry.save()

	def cancel_dle_entry(self):
		if self.items:
			design_ledger_entries = frappe.db.get_all('Design Ledger Entry',{'voucher_type': self.doctype, 'voucher_no': self.name, 'is_cancelled': 0},['name','item_code','warehouse','qty_change'], order_by='name asc')
			if design_ledger_entries:
				for entry in design_ledger_entries:
					frappe.db.set_value('Design Ledger Entry', entry.name, 'is_cancelled', 1)
					actual_qty = frappe.db.get_value('Design Bin', {'item_code': entry.item_code, 'warehouse': entry.warehouse}, 'actual_qty')
					update_qty = actual_qty - entry.qty_change
					frappe.db.set_value('Design Bin', {'item_code': entry.item_code, 'warehouse': entry.warehouse}, 'actual_qty', update_qty)
	
	def item_stock_summary(self):
		unique_list = []
		if self.items:
			for i in self.items:
				if i.item_code not in unique_list:
					#unique item code list for ledger summary
					unique_list.append(i.item_code)
			#set summary item table to empty
			self.set("summary", [])
			for h in unique_list:
				#fetch all revision of item code
				revision = frappe.db.get_all('Revision',
						filters={
							'item_code': h
						},
						fields=['name'],
						order_by='creation desc',
				)
				for dle in revision:
					#fetch dle of each revision
					ledger_entry = frappe.db.get_all('Design Ledger Entry',
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
	def set_status(self):
		if self.entry_type == 'Drawing Transfer':
			self.status = 'Transferred'
		elif self.entry_type == 'Drawing Return':
			self.status = 'Returned'
		elif self.entry_type == 'Drawing Discard':
			self.status = 'Discarded'

	def print_design_drawings_per_item(self, item):
		def create_watermark_canvas(text, page_width, page_height, opacity):
			packet = BytesIO()
			c = canvas.Canvas(packet, pagesize=(page_width, page_height))
			c.setFillColor(lightgrey)
			c.setFont("Helvetica", 16)

				# Calculate the optimal number of columns based on text length
			max_string_width = max([float(c.stringWidth(line, "Helvetica", 16)) for line in text.split('\n')])
			num_columns = min(3, int(float(page_width) / max_string_width))  # Maximum 3 columns
				# Calculate the column spacing
			column_spacing = float(page_width) / num_columns

			for column in range(num_columns):
					# Calculate the x-coordinate for each column
				x = column * column_spacing

					# Calculate the y-coordinate to start at the top and move down
				y = float(page_height)

				lines = text.split('\n')
				line_height = 16  # Initial line height
				for line in lines:
						# Calculate the string width and adjust line height if needed
					string_width = float(c.stringWidth(line, "Helvetica", 18))
					if string_width > column_spacing:
						line_height =  4 # Reduce line height for long text

					while y > 0:
						c.saveState()
						c.translate(float(x), float(y))  # Cast to float to avoid the TypeError
						c.setFillAlpha(opacity)  # Set the opacity
						c.drawString(0, 0, line)
						c.restoreState()
						y -= line_height  # Adjust the vertical spacing based on line height

			c.save()
			packet.seek(0)

			return packet
		if item.item_code:
			file_url = frappe.db.get_value('File', {'attached_to_name': item.item_code}, ['file_url'])
			if file_url:
				file_url = "/home/rehan/frappe-bench/sites/design_dev/public"+file_url
				item.path_c = file_url
				output = "/home/rehan/Output.pdf"
				label = item.t_warehouse
				#start
				packet = io.BytesIO()
				# create a new PDF with Reportlab
				pdf_reader = PdfFileReader(file_url)
				pdf_writer = PdfFileWriter()

				opacity = float(frappe.form_dict.get('opacity', 0.9))
			
				for page_num in range(pdf_reader.getNumPages()):
					# Create a watermark canvas for the current page
					page = pdf_reader.getPage(page_num)
					page_width = page.mediaBox.getWidth()
					page_height = page.mediaBox.getHeight()
					watermark_canvas = create_watermark_canvas(label, page_width, page_height, opacity)

					# Merge the watermark canvas with the current page
					watermark_pdf = PdfFileReader(watermark_canvas)
					watermark_page = watermark_pdf.getPage(0)
					page.mergePage(watermark_page)

					pdf_writer.addPage(page)

				output_pdf = BytesIO()
				pdf_writer.write(output_pdf)
				output_pdf.seek(0)
				outputStream = open("/home/rehan/Output.pdf", "wb")
				pdf_writer.write(outputStream)
				outputStream.close()
				#end
				if item.qty > 0:
					subprocess.run(["lp", "-n", str(item.qty), "-o", item.orientation, "-o", 'media='+item.pdf_print_size, "/home/rehan/Output.pdf"])
					frappe.msgprint('Print')
				else:
					frappe.msgprint('Print Qty Cannot be Zero')
			else:
				frappe.throw('Drawing Not Uploded in Item '+'<b>'+item.item_code)
	# def combine_pdfs(pdf_list):
	# 	pdf_writer = PdfFileWriter()
	# 	for pdf_data in pdf_list:
	# 		pdf_reader = PdfFileReader(BytesIO(pdf_data))
	# 		for page_num in range(pdf_reader.getNumPages()):
	# 			page = pdf_reader.getPage(page_num)
	# 			pdf_writer.addPage(page)

	# 	combined_pdf = BytesIO()
	# 	pdf_writer.write(combined_pdf)
	# 	combined_pdf.seek(0)

	# 	return combined_pdf.getvalue()

@frappe.whitelist()	
def ping():
	return 'pong'

@frappe.whitelist()
def create_discard_entry():
	summary = frappe.db.get_all('Revision Stock Summary', {'parent': frappe.form_dict.design_distribution, 'docstatus': 1}, ['warehouse as s_warehouse', 'item_code', 'revision', 'actual_qty as qty'])

	new_dle_entry = frappe.get_doc({
		"doctype": "Design Distribution",
		"entry_type": 'Drawing Discard',
		"posting_date": frappe.utils.nowdate(),
		"design_distribution": frappe.form_dict.design_distribution,
		"items" : summary
	})
	new_dle_entry.insert(ignore_permissions=True, ignore_mandatory=True)
	new_dle_entry.save()
# @frappe.whitelist()
# def update_received_qty():
# 	received_qty = frappe.db.get_value('Design Distribution Item', frappe.form_dict.id, 'received_qty')
# 	if received_qty:
# 		frappe.db.set_value('Design Distribution Item', frappe.form_dict.id, 'received_qty', frappe.utils.flt(frappe.form_dict.qty) + frappe.utils.flt(received_qty))
# 	else:
# 		frappe.db.set_value('Design Distribution Item', frappe.form_dict.id, 'received_qty', frappe.utils.flt(frappe.form_dict.qty))
# 	return True

# @frappe.whitelist()
# def create_dle_entry():
# 	# Calculate the result based on flag and actual_qty
# 	actual_qty = frappe.db.get_value('Design Bin', {'item_code': frappe.form_dict.item_code, 'warehouse': frappe.form_dict.warehouse}, ['actual_qty'])
# 	result = frappe.utils.flt(frappe.form_dict.qty) + actual_qty if int(frappe.form_dict.flag) == 1 and actual_qty else actual_qty - frappe.utils.flt(frappe.form_dict.qty) if actual_qty else frappe.utils.flt(frappe.form_dict.qty)

# 	# Create a new Design Ledger Entry
# 	new_dle_entry = frappe.get_doc({
# 		"doctype": "Design Ledger Entry",
# 		"item_code": frappe.form_dict.item_code,
# 		"warehouse": frappe.form_dict.warehouse,
# 		"posting_date": frappe.utils.nowdate(),
# 		"posting_time": frappe.utils.nowtime(),
# 		"voucher_type": frappe.form_dict.doctype,
# 		"voucher_no": frappe.form_dict.id,
# 		"qty_change": frappe.utils.flt(frappe.form_dict.qty) if int(frappe.form_dict.flag) == 1 else -frappe.utils.flt(frappe.form_dict.qty),
# 		"qty_after_transaction": result
# 	})

# 	# Insert and save the new Design Ledger Entry
# 	new_dle_entry.insert(ignore_permissions=True, ignore_mandatory=True)
# 	new_dle_entry.save()
# 	return True