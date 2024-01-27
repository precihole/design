import frappe

def get_context(context):
  context.supplier = frappe.db.get_value('Portal User', {'user': frappe.session.user}, 'parent')
  context.permitted_drawings = frappe.db.get_all('Drawing Permission', {'attached_to_name': context.supplier,  'status': ['in', ['Shared', 'Time-Limited Shared']]}, ['name', 'item_code', 'file_url', 'views'])