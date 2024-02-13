# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt
# by SHUBHAM
import frappe
from frappe.model.document import Document
from PyPDF2 import PdfFileWriter, PdfFileReader
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
                    type = "public" if item.new_drawing.startswith("/files") else "private"
                    
                    pdf_file_path = frappe.get_site_path(type, 'files', complete_url.split('/')[-1]);

                    user_signature_path = frappe.get_site_path('public', 'files', self.approved_by  + ".png");
                    modified_signature_path = user_signature_path.replace(".com", "")

                    # Create a watermarked PDF (using the same file name and path)
                    watermarked_pdf_path = pdf_file_path
                    # self.add_watermark(pdf_file_path, self.approved_by , user_signature_path, watermarked_pdf_path)   
                    replacements = [("APPROVED BY", self.approved_by )]
                    self.replace_text(pdf_file_path, replacements, watermarked_pdf_path)

    def replace_text(self,pdf_path, replacements, output_path):
        doc = fitz.open(pdf_path)

        for page in doc:  # Iterate through each page
            for old_text, new_text in replacements:
                text_instances = page.search_for(old_text)
                for inst in text_instances:
          
            # This might need adjusting depending on where you want the text
                    text_x = inst.x1   # Add a small margin to the right of the keyword
                    text_y = inst.y1

                    # Add the new text at the calculated position
                    page.insert_text((text_x, text_y), new_text, fontname="helv", fontsize=12)

            # Check if the output path is the same as the input path
        if pdf_path == output_path:
            # Save using incremental saving
            doc.save(output_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        else:
            # Save to a new file
            doc.save(output_path)

    

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
                if frappe.db.get_single_value('Design Print Settings', 'new_drawing_pdf_required') == 1 :
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
    



    
