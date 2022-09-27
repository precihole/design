# Copyright (c) 2022, Precihole and contributors
# For license information, please see license.txt

import frappe
import os
import subprocess, sys
import tempfile
from frappe.model.document import Document

class PrintDoc(Document):
	def before_save(self):
		self.validation()
	#set Default Printer
	def validation(self):
		if self.default == self.printer_list:
			frappe.throw('<b>'+self.default+' </b>Already Set')
	#printerDoc		
	# def print_multiple_doc(self):
	# 	subprocess.run(["lp", "/home/user/test"])
@frappe.whitelist()
def get_printer_list():
	printer_list = subprocess.run(args = ['lpstat', '-d', '-a'],
								universal_newlines = True,
								stdout = subprocess.PIPE)
	nmap_lines = printer_list.stdout.splitlines()
	frappe.response['message']={
		'data':nmap_lines
	}