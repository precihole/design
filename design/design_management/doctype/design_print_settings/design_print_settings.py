# Copyright (c) 2023, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import subprocess, sys

class DesignPrintSettings(Document):
	pass

@frappe.whitelist()
def fetch_printer_information():
	printer_command_result = subprocess.run(args=['lpstat', '-d', '-a'], universal_newlines=True, stdout=subprocess.PIPE)
	system_printer_lines = printer_command_result.stdout.splitlines()
	return {'data': system_printer_lines}

@frappe.whitelist()
def check_printer_status():
	ip_address = frappe.form_dict.ip_address

	command = ["ping", "-c", "4", ip_address]
	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	print("Ping Output:")
	print(result.stdout)

	print("\nError Output:")
	print(result.stderr)

	if result.returncode == 0:
		frappe.msgprint("Ping command executed successfully.")
	else:
		frappe.msgprint(f"Ping command failed with return code {result.returncode}.")

@frappe.whitelist()
def set_default_printer():
	printer_name = frappe.form_dict.printer_name
	
	command = ["lpoptions", "-d", printer_name]
	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		frappe.msgprint(f"Default printer set to {printer_name}.")
	else:
		frappe.msgprint(f"Failed to set default printer. Error: {result.stderr}.")

#fetch ip address -> lpstat -v

