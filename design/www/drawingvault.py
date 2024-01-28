import frappe

def get_context(context):
  context.supplier = frappe.db.get_value('Portal User', {'user': frappe.session.user}, 'parent')

  context.drawing_permission_names = frappe.db.get_all(
      'Drawing Permission',
      {'attached_to_name': context.supplier, 'status': 'Shared'},
      pluck='name'
  )

  context.drawing_permission_details = frappe.db.get_all(
      'Drawing Permission Item',
      {'parent': ['in', context.drawing_permission_names]},
      ['name', 'item_code', 'file_url', 'views']
  )
