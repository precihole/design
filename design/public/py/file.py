import frappe

def upload_file_using_zip(doc, method):
    if frappe.session.user == "Administrator":
        file_name = doc.file_name
        # Splitting the file name based on the underscore
        parts = file_name.split('_')

        # Extracting the item code (the first part before the underscore)
        item_code = parts[0]
        
        doc.attached_to_doctype = 'Item'
        doc.attached_to_name = item_code