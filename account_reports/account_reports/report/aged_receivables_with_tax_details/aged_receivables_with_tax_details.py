# Copyright (c) 2013, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	customer_details=get_customer_conditions(filters)
	gl_entries = get_tax_outstanding_details(filters)
	
	data = []
	
	return columns, gl_entries


def get_columns():
	return [_("Name") + ":Link/Customer:150", _("Amount Outstanding") + ":Currency:150",  _("Tax Outstanding") + ":Currency:150"]

def get_tax_outstanding_details(filters):
	return frappe.db.sql(""" select party,ifnull(sum(outstanding_amount),0) , ifnull(sum(outstanding_tax_amount),0) from `tabAccounts Receivables With Tax`
							where voucher_type ='Sales Invoice' and {sle_conditions} group by party"""\
							.format(sle_conditions=get_customer_conditions(filters)), as_list=1)


def get_customer_conditions(filters):
	conditions = []
	if filters.get("company"):
		conditions.append("company='%(company)s'"%filters)
	if filters.get("customer"):
		conditions.append("party='%(customer)s'"%filters)

	return " {}".format(" and ".join(conditions)) if conditions else ""