# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import _
from datetime import date, timedelta
from erpnext.accounts.utils import get_balance_on
#class FiscalYearError(frappe.ValidationError): pass

def execute(filters=None):
	account_details = {}
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	columns = get_columns()

	res = get_result(filters, account_details)

	return columns, res

def validate_filters(filters, account_details):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_columns():
	return [_("Posting Date") + ":Date:90", _("Account") + ":Link/Account:200",_("Opening") + ":Float:100", 
		_("Debit") + ":Float:100", _("Credit") + ":Float:100",
		_("Closing") + ":Float:100",_("Net Activity") + ":Float:100" ,
		_("Src") + "::120", _("Memo") + ":Dynamic Link/Voucher Type:160",_("Job#") + "::150"]

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)
	
	data = get_data_with_opening_closing(filters, account_details, gl_entries)

	result = get_result_as_list(data)

	return result

def get_gl_entries(filters):

	gl_entries = frappe.db.sql("""select posting_date, account,
		sum(ifnull(debit, 0)) as debit, sum(ifnull(credit, 0)) as credit,
		voucher_type, voucher_no,party
		from `tabGL Entry`
		where company=%(company)s {conditions}  
		and posting_date <= %(to_date)s or ifnull(is_opening, 'No') = 'Yes'
		group by account
		order by posting_date , account"""\
		.format(conditions=get_conditions(filters)),
		filters ,as_dict=1)

	openind_date= getdate(filters.get("from_date"))
	date=openind_date-timedelta(days=1)
	if gl_entries:
		for i in gl_entries:
			if i.get("account"):
				opening_bal=get_balance_on(i.get("account"),date,party=None,party_type=None)
				i['opening']=opening_bal
				if i['opening']<0:
					i['opening']*=(-1)
				closing_bal=get_balance_on(i.get("account"),filters.get("to_date"),party=None,party_type=None)
				i['closing']=closing_bal
				if i['closing']<0:
					i['closing']*=(-1)


	return gl_entries

def get_conditions(filters):
	conditions = []
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))
		
	if not (filters.get("account") or filters.get("party") or filters.get("group_by_account")):
		conditions.append("posting_date >=%(from_date)s")

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("GL Entry")
	if match_conditions: conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []
	gle_map = initialize_gle_map(gl_entries)
	opening, total_debit, total_credit, gle_map = get_accountwise_gle(filters, gl_entries, gle_map)
	
	# Opening for filtered account
	if filters.get("account") or filters.get("party"):
		data += [get_balance_row(_("Opening"), opening), {}]
	
	for acc, acc_dict in gle_map.items():
		if acc_dict.entries:
			# Opening for individual ledger, if grouped by account
			if filters.get("group_by_account"):
				data.append(get_balance_row(_("Opening"), acc_dict.opening))

			data += acc_dict.entries
			# Totals and closing for individual ledger, if grouped by account
			if filters.get("group_by_account"):
				data += [{"account": "'" + _("Totals") + "'", "debit": acc_dict.total_debit,
					"credit": acc_dict.total_credit},
					get_balance_row(_("Closing (Opening + Totals)"),
						(acc_dict.opening + acc_dict.total_debit - acc_dict.total_credit)), {}]

	# Total debit and credit between from and to date
	if total_debit or total_credit:
		data.append({"account": "'" + _("Totals") + "'", "debit": total_debit, "credit": total_credit})

	# Closing for filtered account
	if filters.get("account") or filters.get("party"):
		data.append(get_balance_row(_("Closing (Opening + Totals)"),
			(opening + total_debit - total_credit)))

	return data

def initialize_gle_map(gl_entries):
	gle_map = frappe._dict()
	for gle in gl_entries:
		gle_map.setdefault(gle.account, frappe._dict({
			"opening": 0,
			"entries": [],
			"total_debit": 0,
			"total_credit": 0,
			"closing": 0
		}))
	return gle_map

def initialize_gle_map(gl_entries):
	gle_map = frappe._dict()
	for gle in gl_entries:
		gle_map.setdefault(gle.account, frappe._dict({
			"opening": 0,
			"entries": [],
			"total_debit": 0,
			"total_credit": 0,
			"closing": 0
		}))
	return gle_map

def get_accountwise_gle(filters, gl_entries, gle_map):
	opening, total_debit, total_credit = 0, 0, 0
	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		amount = flt(gle.debit, 3) - flt(gle.credit, 3)
		
		if (filters.get("account") or filters.get("party") or filters.get("group_by_account")) \
				and (gle.posting_date < from_date or cstr(gle.is_opening) == "Yes"):
			gle_map[gle.account].opening += amount
			if filters.get("account") or filters.get("party"):
				opening += amount
		
		elif gle.posting_date <= to_date:
			gle_map[gle.account].entries.append(gle)
			gle_map[gle.account].total_debit += flt(gle.debit, 3)
			gle_map[gle.account].total_credit += flt(gle.credit, 3)

			total_debit += flt(gle.debit, 3)
			total_credit += flt(gle.credit, 3)

	
	return opening, total_debit, total_credit, gle_map

def get_balance_row(label, balance):
	return {
		"account": "'" + label + "'",
		"debit": balance if balance > 0 else 0,
		"credit": -1*balance if balance < 0 else 0,
	}

def get_result_as_list(data):
	result = []
	cnt = 1
	
	for d in data:
		net_activity = None
		
		if len(data) - 1 >= cnt :
			if d.get("debit") == 0:
				
				if d.get("credit") == 0:
					net_activity = 0.0
				
				elif d.get("credit") > 0:
					net_activity = d.get("credit")
			
			elif d.get("debit") > 0:
				
				if d.get("credit") == 0:
					net_activity = d.get("debit")
				
				elif d.get("credit") > 0:
					net_activity = d.get("debit")-d.get("credit")
					if net_activity < 0:
						net_activity = (-1)* net_activity
			
		result.append([d.get("posting_date"), d.get("account"), d.get("opening"), d.get("debit"), d.get("credit"),
			d.get("closing"),net_activity,d.get("voucher_type"),d.get("voucher_no"),d.get("party") ])

		cnt += 1

	return result
