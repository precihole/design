# Copyright (c) 2022, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DMRN(Document):
	pass
	def on_submit(self):
		if self.dmrn_details:
			for i in self.dmrn_details:
				if i.drawing_no:
					item_doc = frappe.get_doc("Item",  i.drawing_no)
					item_doc.revision_c = i.rev_no
					item_doc.save()