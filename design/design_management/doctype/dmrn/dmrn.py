# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt
# by SHUBHAM
import frappe
from frappe.model.document import Document
# from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from io import BytesIO
import fitz  # PyMuPDF

class DMRN(Document):

    def on_update(self):
        if self.workflow_state == "Approved" and self.dmrn_details:
            for item in self.dmrn_details:
                if item.new_drawing:
                    approved_by_fullname = frappe.session.user
                    complete_url = item.new_drawing
                    pdf_file_path = frappe.db.get_single_value('Design Print Settings', 'public') + complete_url

                    user_signature_path = frappe.db.get_single_value('Design Print Settings', 'public') + "/files/" + self.approved_by + ".png"
                    modified_signature_path = user_signature_path.replace(".com", "")

                    # Create a watermarked PDF (using the same file name and path)
                    watermarked_pdf_path = pdf_file_path
                    self.add_watermark(pdf_file_path, approved_by_fullname, modified_signature_path, watermarked_pdf_path)

    def add_watermark(self, pdf_file_path, text_watermark, image_watermark_path, output_path):
        # Open the original PDF using PyMuPDF
        original_doc = fitz.open(pdf_file_path)

        with open(pdf_file_path, 'rb') as original_file:
            original_pdf = PdfFileReader(original_file)

            # Create a BytesIO buffer to store the modified PDF
            output_buffer = BytesIO()
            output_pdf = PdfFileWriter()

            for page_num in range(len(original_pdf.pages)):
                original_page = original_pdf.pages[page_num]

                # Get dimensions of the page using PyMuPDF
                page_width = int(original_page.mediaBox.upperRight[0])
                page_height = int(original_page.mediaBox.upperRight[1])
                
                # Create a new BytesIO buffer for each page
                watermark_buffer = BytesIO()

                # Create a watermark canvas for the current page
                watermark_canvas = canvas.Canvas(watermark_buffer, pagesize=(page_width, page_height))
                self.draw_watermark(watermark_canvas, image_watermark_path, text_watermark, page_width, page_height)
                watermark_pdf = PdfFileReader(watermark_buffer)
                watermark_page = watermark_pdf.pages[0]

                # Merge the watermark canvas with the current page
                original_page.merge_page(watermark_page)

                # Add the modified page to the new PDF buffer
                output_pdf.addPage(original_page)

            # Save the watermarked PDF to the output buffer
            output_pdf.write(output_buffer)
            output_buffer.seek(0)

            # Save the buffer to the specified output path
            with open(output_path, 'wb') as output_file:
                output_file.write(output_buffer.read())



    def draw_watermark(self, canvas, image_path, text, page_width, page_height):
        # Set font and size for text watermark
        canvas.setFont("Helvetica", 16)
        
        # Draw the watermark text on the canvas
        text_width = int(canvas.stringWidth(text, "Helvetica", 16))
        text_height = 26

        text_x = int(page_width - text_width - 20)
        #text_y = int(img_y + img_height + 10)
        text_y = int(20)
        canvas.drawString(text_x, text_y, text)

        # Draw the transparent image on the canvas
        img_width = 100
        img_height = 50

        img_x = int(page_width - img_width - 20)
        img_y = int(20)
        img_y = int(text_y + text_height + 20)
        canvas.drawImage(image_path, img_x, img_y, width=img_width, height=img_height, mask='auto')
        canvas.save()



###########################################################################################################################
#by rehan
    
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
    



    
