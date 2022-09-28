# Copyright (c) 2022, Precihole and contributors
# For license information, please see license.txt

import frappe
import os
import subprocess, sys
import tempfile
from frappe.model.document import Document
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class PrintDoc(Document):
	def on_submit(self):	
		if self.child:
			for i in self.child:
				if i.item_code:
					file_url = frappe.db.get_value('File', {'attached_to_name': i.item_code}, ['file_url'])
					if file_url:
						file_url = "/home/user/ERPNext/frappe-bench/sites/preciholesports.com/public"+file_url
						i.path_c = file_url
						output = "/home/user/Pictures/output.pdf"
						label = i.dept
						#start
						packet = io.BytesIO()
						# create a new PDF with Reportlab
						can = canvas.Canvas(packet, pagesize=letter)
						can.drawString(100, 100, label)
						can.save()

						# move to the beginning of the StringIO buffer
						packet.seek(0)
						new_pdf = PdfFileReader(packet)
						# read your existing PDF
						existing_pdf = PdfFileReader(open(file_url, "rb"))
						output = PdfFileWriter()
						# add the "watermark" (which is the new pdf) on the existing page
						page = existing_pdf.getPage(0)
						page2 = new_pdf.getPage(0)
						page.mergePage(page2)
						output.addPage(page)
						# finally, write "output" to a real file
						outputStream = open("/home/user/Pictures/output.pdf", "wb")
						output.write(outputStream)
						outputStream.close()
						#end
						if i.qty >= 1:
							subprocess.run(["lp", "-n", str(i.qty), "-o", i.orientation_c, "-o", 'media='+i.pdf_print_size, "/home/user/Pictures/output.pdf"])
						else:
							frappe.msgprint('Print Qty Cannot be Zero')
					else:
						frappe.throw('Drawing Not Uploded in Item '+'<b>'+i.item_code)

@frappe.whitelist()
def get_printer_list():
	printer_list = subprocess.run(args = ['lpstat', '-d', '-a'],
								universal_newlines = True,
								stdout = subprocess.PIPE)
	nmap_lines = printer_list.stdout.splitlines()
	frappe.response['message']={
		'data':nmap_lines
	}

@frappe.whitelist()
def get_printer_status():
	status = subprocess.run(args = ['lpq'],
								universal_newlines = True,
								stdout = subprocess.PIPE)
	printer_status = status.stdout.splitlines()
	frappe.response['message']={
		'data':printer_status
	}