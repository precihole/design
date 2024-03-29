# Copyright (c) 2023, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import subprocess, sys
import tempfile
# from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import lightgrey
import json
from frappe.utils.pdf import get_pdf

class DesignDistribution(Document):
	def before_save(self):
		self.custom_validations()
		if self.entry_type == 'Drawing Transfer':
			self.item_stock_summary()

	def before_submit(self):
		self.set_status()

	def on_submit(self):
		def download_pdf(doctype, name, format=None, doc=None):
			# this is to get dmrn print
			html = frappe.get_print(doctype, name, format, doc=doc)
			pdf_content = get_pdf(html)

			# Specify the full path where you want to save the PDF file
			pdf_path = "/home/erpadmin/frappe-bench/sites/preciholesports/public/files/output.pdf"

			# Save the PDF file
			with open(pdf_path, "wb") as pdf_file:
				pdf_file.write(pdf_content)
			# return frappe.msgprint("printing")
			return subprocess.run(["lp", "-n", "1", "-o", "Potrait", "-o", 'media=A4', pdf_path])
		# def download_pdf(doctype, name, format=None,doc= None,no_letterhead=0, language=None, letterhead=None):
		# 	# frappe.throw(str(doctype))
		# 	html = frappe.get_print(doctype, name, format, doc=doc, as_pdf=True, letterhead=letterhead, no_letterhead=no_letterhead)
		# 	pdf_content = get_pdf(html)

		# 	# Specify the full path where you want to save the PDF file
		# 	pdf_path = "/home/erpadmin/frappe-bench/sites/preciholesports/public/files/pdf_file.pdf"

		# 	# Save the PDF file
		# 	with open(pdf_path, "wb") as pdf_file:
		# 		pdf_file.write(pdf_content)
		# 	return frappe.msgprint("done")
		# 	# return subprocess.run(["lp", "-n", "1", "-o", "Potrait", "-o", 'media=A4', pdf_path])	
		if self.items:
			check_warehouse = None
			for item in self.items:
				if self.entry_type == 'Drawing Transfer':
					# Produce design quantities
					self.produceDesignQuantities(item)
					# Transfer to Target
					self.transferQuantities(item)
					if check_warehouse != None and check_warehouse != item.t_warehouse:
						frappe.msgprint('Print Blank')
						subprocess.run(["lp", "/home/rehan/Downloads/blank.pdf"])
					self.print_design_drawings_per_item(item)
					check_warehouse = item.t_warehouse

				elif self.entry_type == "Drawing Return":
					# Transfer to Target
					self.transferQuantities(item)

				elif self.entry_type == "Drawing Discard":
					self.discardDesignQuantities(item)
				# get dmrn of item if there is then print it with item
				get_drmn = frappe.db.get_value("DMRN Detail",{"item_code":item.item_code,"new_revision":item.revision},"parent")	
				# This is to update pdf
				if get_drmn:
					download_pdf("DMRN",str(get_drmn))
		

	def on_cancel(self):
		self.cancel_dle_entry()

	def custom_validations(self):
		for item in self.items:
			if item.s_warehouse == item.t_warehouse:
				frappe.throw(("Source and target warehouse cannot be the same for row {0}").format(item.idx))
			if item.qty == 0:
				frappe.throw(("Row {0}: Qty is mandatory").format(item.idx), title=("Zero quantity"))
			if self.entry_type != "Drawing Transfer":
				qty = frappe.db.get_value('Design Ledger Entry', {'item_code': item.item_code, 'warehouse': item.s_warehouse, 'revision_no': item.revision, 'is_cancelled': 0}, ['qty_after_transaction']) or 0
				if item.qty > qty:
					frappe.throw('No qty available')

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
			file_url = frappe.db.get_value('File', {'attached_to_doctype': 'Item', 'attached_to_name': item.item_code}, ['file_url'])
			if file_url:
				file_url = frappe.db.get_single_value('Design Print Settings', 'public') + file_url
				output = frappe.db.get_single_value('Design Print Settings', 'output')
				label = item.t_warehouse
				#start
				packet = io.BytesIO()
				# create a new PDF with Reportlab
				pdf_reader = PdfFileReader(file_url)
				pdf_writer = PdfFileWriter()
				opacity = frappe.db.get_single_value('Design Print Settings', 'opacity')
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
				outputStream = open(frappe.db.get_single_value('Design Print Settings', 'output'), "wb")
				pdf_writer.write(outputStream)
				outputStream.close()
				#end
				
				# Check if item.orientation is present
				if item.orientation:
					orientation_option = item.orientation
				else:
					default_orientation = frappe.db.get_single_value('Design Print Settings', 'orientation')
					orientation_option = default_orientation
					
				# Check if item.paper_size is present
				if item.paper_size:
					paper_size_option = item.paper_size
				else:
					default_paper_size_option = frappe.db.get_single_value('Design Print Settings', 'paper_size')
					paper_size_option = default_paper_size_option

				if item.qty > 0:
					# subprocess.run(["lp", "-n", str(item.qty), orientation_option, paper_size_option, "/home/rehan/Output.pdf"])
					subprocess.run(["lp", "-n", str(item.qty), "-o", orientation_option, "-o", 'media=' + paper_size_option, frappe.db.get_single_value('Design Print Settings', 'output')])
					# frappe.msgprint('Printing')
				else:
					frappe.msgprint('Print qty cannot be zero')
			else:
				frappe.throw(f'Drawing Not Uploaded in Item <b>{item.item_code}</b>')

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
	frappe.msgprint(f'Discard entry Created <a href="{frappe.utils.get_url()}/app/design-distribution/{new_dle_entry.name}">{new_dle_entry.name}</a>')
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
