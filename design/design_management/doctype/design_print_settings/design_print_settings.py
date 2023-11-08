# Copyright (c) 2023, Precihole and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import subprocess, sys

class DesignPrintSettings(Document):
	pass

@frappe.whitelist()
def get_printer_list():
	printer_list = subprocess.run(args = ['lpstat', '-d', '-a'], universal_newlines = True, stdout = subprocess.PIPE)
	nmap_lines = printer_list.stdout.splitlines()
	frappe.response['message']={
		'data': nmap_lines
	}

@frappe.whitelist()
def get_printer_status():
	# Define the command as a list of strings
	ip_address = frappe.form_dict.ip_address
	command = ["ping", "-c", "4", ip_address]

	# Run the ping command
	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	# Print the output and error, if any
	print("Ping Output:")
	print(result.stdout)

	print("\nError Output:")
	print(result.stderr)

	# Check the return code
	if result.returncode == 0:
		frappe.msgprint("Ping command executed successfully.")
	else:
		frappe.msgprint(f"Ping command failed with return code {result.returncode}.")