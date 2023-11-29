# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
import os
import subprocess, sys
import tempfile
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfReader, PdfWriter
import io
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import lightgrey
import json
from frappe.utils.pdf import get_pdf

class DMRN(Document):


    def on_update(self):
       # frappe.throw("hskdjfkldjsfsdjklfmsdklfj")
        # Check if the document is in the "Draft" workflow state
        if self.workflow_state == "Approved" and self.dmrn_details:
            frappe.throwE('HIII ERROR')
            for item in self.dmrn_details:
                if item.new_drawing:
                    # Get the full name from the "approved_by" field in the parent document
                    approved_by_fullname = self.approved_by

                    # Construct the complete URL by appending the dynamic path
                    complete_url = item.new_drawing

                    # Get the path on the server
                    pdf_file_path = frappe.db.get_single_value('Design Print Settings', 'public') + complete_url
                    #frappe.msgprint(f"Generated PDF file path: {pdf_file_path}")

                    # Create a watermarked PDF (using the same file name and path)
                    watermarked_pdf_path = pdf_file_path
                    self.add_watermark(pdf_file_path, approved_by_fullname, watermarked_pdf_path)
                    #frappe.msgprint(f"Generated watermarked PDF file path: {watermarked_pdf_path}")

                    # Delete the original PDF
                    #frappe.delete_file(item.new_drawing)

                    # Upload the watermarked PDF to the same URL
                    #frappe.uploadfile(file_url=complete_url, content=frappe.read_file(watermarked_pdf_path))

    def add_watermark(self, pdf_file_path, watermark_text, output_path):
        with open(pdf_file_path, 'rb') as original_file:
            original_pdf = PdfReader(original_file)

            # Create a BytesIO buffer to store the modified PDF
            output_buffer = BytesIO()
            output_pdf = PdfFileWriter()

            for page_num in range(len(original_pdf.pages)):
                original_page = original_pdf.pages[page_num]

                # Create a watermark canvas for the current page
                watermark_canvas = canvas.Canvas(BytesIO())
                self.draw_watermark(watermark_canvas, watermark_text)

                # Merge the watermark canvas with the current page
                watermark_pdf = PdfReader(BytesIO(watermark_canvas.getpdfdata()))
                watermark_page = watermark_pdf.pages[0]
                original_page.merge_page(watermark_page)

                # Add the modified page to the new PDF buffer
                output_pdf.addPage(original_page)

            # Save the watermarked PDF to the output buffer
            output_pdf.write(output_buffer)
            output_buffer.seek(0)

            # Save the buffer to the specified output path
            with open(output_path, 'wb') as output_file:
                output_file.write(output_buffer.read())

    def draw_watermark(self, canvas, text):
        # Set font and size
        canvas.setFont("Helvetica", 26)

        # Draw the watermark text on the canvas
        canvas.drawString(350, 100, text)
        canvas.save()
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

    
    def before_save(self):
        #frappe.throw("your can not save")
        self.custom_validations()
    
    def before_submit(self):
        for item in self.dmrn_details:
            self.fetch_old_revision(item)
       
        if self.workflow_state == "Approved":
            self.approved_by = frappe.session.user
    
    def on_submit(self):
        self.update_new_revision()
        for item in self.dmrn_details:
            self.link_new_drawing(item)
    
    def on_cancel(self):
        self.delete_revision()
        self.update_old_revision()
    
    def custom_validations(self):
        if self.dmrn_details:
            for item in self.dmrn_details:
                # new drawing validation
                if self.get('__islocal') == None and not item.new_drawing:
                    frappe.throw(f'New Drawing is mandatory in {item.item_code}')
                    
                old_revision = frappe.db.get_value('Item', item.item_code, 'revision_c')
                if old_revision:
                    if item.new_revision:
                        if item.new_revision == old_revision:
                            frappe.throw(f"Revision is already at {item.new_revision} in <b>{item.item_code}</b>")
                    else:
                        frappe.throw(f"New revision cannot be empty in <b>{item.item_code}</b>")
                else:
                    frappe.throw(f"Revision is empty in Item Master <b>{item.item_code}</b>")
    
    def fetch_old_revision(self, item):
        old_revision = frappe.db.get_value('Item', item.item_code, 'revision_c')
        if old_revision:
            item.old_revision = old_revision
    
    def update_new_revision(self):
        if self.dmrn_details:
            for item in self.dmrn_details:
                if item.item_code and item.new_revision:
                    doc = frappe.get_doc("Item", item.item_code)
                    doc.revision_c = item.new_revision
                    doc.save()
                    revision_entry = frappe.get_doc({
                        "doctype": "Revision",
                        "revision": item.new_revision,
                        "item_code": item.item_code,
                        "reference_no": self.name,
                        "description": "This is an automatic entry from DMRN"
                    }).insert(ignore_permissions=True, ignore_mandatory=True)
                    revision_entry.save()
    
    def link_new_drawing(self, item):
        # delete old drawing
        frappe.db.delete("File", {"attached_to_doctype": 'Item', 'attached_to_name': item.item_code})
    
        all_drawings = frappe.get_all("File", {'attached_to_doctype': self.doctype, 'attached_to_name': self.name, 'file_url': item.new_drawing}, ['file_name', 'file_url', 'file_size', 'file_type', 'is_private'])
        for drawing in all_drawings:
            link_drawing_to_item = frappe.get_doc({
                "doctype": "File",
                "file_name": drawing.file_name,
                "file_url": drawing.file_url,
                "file_size": drawing.file_size,
                "file_type": drawing.file_type,
                "is_private": drawing.is_private,
                "attached_to_doctype": "Item",
                "attached_to_name": item.item_code
            })
            link_drawing_to_item.insert(ignore_permissions=True, ignore_mandatory=True)
        # delete new drawing from DMRN
        frappe.db.delete("File", {"attached_to_doctype": self.doctype, 'attached_to_name': self.name, 'file_url': item.new_drawing})
    
    def delete_revision(self):
        frappe.db.delete("Revision", {"reference_no": self.name})
    
    def update_old_revision(self):
        if self.dmrn_details:
            for item in self.dmrn_details:
                if item.item_code and item.old_revision:
                    frappe.db.set_value('Item', item.item_code, 'revision_c', item.old_revision)
    



    