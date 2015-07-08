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
	data=[]
	outstanding_amount=frappe.db.sql("""select party, ifnull(sum(outstanding_amount),0) from `tabAccounts Receivables With Tax` 
		where account='Debtors - F' and voucher_type='Sales Invoice' and {sle_conditions} group by party"""\
							.format(sle_conditions=get_customer_conditions(filters)), as_list=1)

	if outstanding_amount:
		for i in outstanding_amount:
			outstanding_tax_amount= frappe.db.sql("""select ifnull(sum(outstanding_tax_amount),0) from `tabAccounts Receivables With Tax` 
												where account!='Debtors - F' and party='%s' and voucher_type='Sales Invoice' and company='%s' and fiscal_year='%s'"""
												%(i[0],filters.get("company"),filters.get("fiscal_year")) ,as_list=1)
			if outstanding_tax_amount:
				i.append(outstanding_tax_amount[0][0])
				data.append(i)

	return data

def get_customer_conditions(filters):
	conditions = []
	if filters.get("company"):
		conditions.append("company='%(company)s'"%filters)
	if filters.get("customer"):
		conditions.append("party='%(customer)s'"%filters)
	if filters.get("fiscal_year"):
		conditions.append("fiscal_year='%(fiscal_year)s'"%filters)

	return " {}".format(" and ".join(conditions)) if conditions else ""