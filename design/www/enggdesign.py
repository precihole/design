import frappe

def get_context(context):
    context.draw = frappe.db.get_value('Drawing Permission', frappe.form_dict.get('query'), ['file_url', 'attached_to_name', 'allow_download', 'status'])