# Copyright (c) 2013, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import (flt,cint,cstr, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)
import datetime
from frappe import _, _dict



def execute(filters=None):
	
	period_list,period_list_last_year = get_period_list(filters,filters.fiscal_year, filters.month, from_beginning=True)

	columns = []
	data = []
	
	asset = get_data(filters.company, "Asset", "Debit", period_list)
	asset1 = get_data(filters.company, "Asset", "Debit", period_list_last_year)

	
	liability = get_data(filters.company, "Liability", "Credit", period_list)
	liability1 = get_data(filters.company, "Liability", "Credit", period_list_last_year)

	equity = get_data(filters.company, "Equity", "Credit", period_list)
	equity1 = get_data(filters.company, "Equity", "Credit", period_list_last_year)

	
	provisional_profit_loss = get_provisional_profit_loss(asset, liability, equity, period_list)
	provisional_profit_loss1 = get_provisional_profit_loss(asset1, liability1, equity1, period_list_last_year)

	data = []
	data1 = []
	result =[]
	data.extend(asset  or [])
	data.extend(liability  or [])
	data.extend(equity or [])

	data1.extend(asset1 or [])
	data1.extend(liability1 or [])
	data1.extend(equity1 or [])

	if provisional_profit_loss:
		data.append(provisional_profit_loss)
	if provisional_profit_loss1:
		data1.append(provisional_profit_loss1)

	columns = get_columns(period_list,period_list_last_year)

	result= get_result_as_list(data,data1,period_list,period_list_last_year)

	return columns,result

def get_period_list(filters,fiscal_year, month, from_beginning=False):
	import datetime
	
	"""Get a list of dict {"to_date": to_date, "key": key, "label": label}
		Periodicity can be (Yearly, Quarterly, Monthly)"""

	fy_start_end_date = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"])
	if not fy_start_end_date:
		frappe.throw(_("Fiscal Year {0} not found.").format(fiscal_year))


	start_date = getdate(fy_start_end_date[0])
	end_date = getdate(fy_start_end_date[1])
	
	to_date = get_first_day(start_date)

	from calendar import monthrange

	filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(filters["month"]) +1
	

	year= cint(filters["fiscal_year"].split("-")[-1]) -1
	last_fiscal_year= (cint(filters["fiscal_year"].split("-")[-1])) -2 
	last_fiscal_year1 =(cint(filters["fiscal_year"].split("-")[-1])) -1
	last_year = cstr(last_fiscal_year) +'-'+ cstr(last_fiscal_year1)
	date1= '04-01-'+last_year
	start_date_last_year = getdate(date1)

	if month=='Jan':
		end_date='31-01-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-01-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Feb':
		end_date='28-02-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '28-02-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Mar':
		end_date='31-03-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-03-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Apr':
		end_date='30-04-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '30-04-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='May':
		end_date='31-05-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-05-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Jun':
		end_date='30-06-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '30-06-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Jul':
		end_date='31-07-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-07-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Aug':
		end_date='31-08-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-08-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Sep':
		end_date='30-09-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '30-09-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Oct':
		end_date='31-10-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-10-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Nov':
		end_date='30-11-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '30-11-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)

	elif month=='Dec':
		end_date='31-12-'+cstr(year)
		end_date1 = getdate(end_date)
		last_year_to_date = '31-12-'+cstr(last_year)
		last_year_to_date1 = getdate(last_year_to_date)


	period_list=[]

	period_list_last_year =[]

	period_list.append(_dict({ "to_date": end_date1 }))

	period_list_last_year.append(_dict({ "to_date": last_year_to_date1 }))

	for opts in period_list:
		opts.update({
			"key": fiscal_year,
			"label": 'This Year',
			"year_start_date": start_date,
			"year_end_date": end_date1
		})

		if from_beginning:
			# set start date as None for all fiscal periods, used in case of Balance Sheet
			opts["from_date"] = None
		else:
			opts["from_date"] = start_date


	for optss in period_list_last_year:
		optss.update({
			"key": last_year,
			"label": 'Last Year',
			"year_start_date": start_date_last_year,
			"year_end_date": last_year_to_date1
		})

		if from_beginning:
			# set start date as None for all fiscal periods, used in case of Balance Sheet
			optss["from_date"] = None
		else:
			optss["from_date"] = start_date_last_year

	
	return period_list ,period_list_last_year

def get_data(company, root_type, balance_must_be, period_list, ignore_closing_entries=False):
	accounts = get_accounts(company, root_type)

	if not accounts:
		return None

	accounts, accounts_by_name = filter_accounts(accounts)
	gl_entries_by_account = get_gl_entries(company, period_list[0]["from_date"], period_list[0]["to_date"],
		accounts[0].lft, accounts[0].rgt, ignore_closing_entries=ignore_closing_entries)

	calculate_values(accounts_by_name, gl_entries_by_account, period_list)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list)
	out = prepare_data(accounts, balance_must_be, period_list)

	if out:
		add_total_row(out, balance_must_be, period_list)

	return out


def get_accounts(company, root_type):
	return frappe.db.sql("""select name, parent_account, lft, rgt, root_type, report_type, account_name from `tabAccount`
		where company=%s and root_type=%s order by lft""", (company, root_type), as_dict=True)

def filter_accounts(accounts, depth=10):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			if parent == None:
				sort_root_accounts(children)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)
	return filtered_accounts, accounts_by_name

def sort_root_accounts(roots):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_roots(a, b):
		if a.report_type != b.report_type and a.report_type == "Balance Sheet":
			return -1
		if a.root_type != b.root_type and a.root_type == "Asset":
			return -1
		if a.root_type == "Liability" and b.root_type == "Equity":
			return -1
		if a.root_type == "Income" and b.root_type == "Expense":
			return -1
		return 1

	roots.sort(compare_roots)


def get_gl_entries(company, from_date, to_date, root_lft, root_rgt, ignore_closing_entries=False):
	"""Returns a dict like { "account": [gl entries], ... }"""
	additional_conditions = []

	if ignore_closing_entries:
		additional_conditions.append("and ifnull(voucher_type, '')!='Period Closing Voucher'")

	if from_date:
		additional_conditions.append("and posting_date >= %(from_date)s")

	gl_entries = frappe.db.sql("""select posting_date, account, debit, credit, is_opening from `tabGL Entry`
		where company=%(company)s
		{additional_conditions}
		and posting_date <= %(to_date)s
		and account in (select name from `tabAccount`
			where lft >= %(lft)s and rgt <= %(rgt)s)
		order by account, posting_date""".format(additional_conditions="\n".join(additional_conditions)),
		{
			"company": company,
			"from_date": from_date,
			"to_date": to_date,
			"lft": root_lft,
			"rgt": root_rgt
		},
		as_dict=True)

	gl_entries_by_account = {}
	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.account, []).append(entry)

	return gl_entries_by_account


def calculate_values(accounts_by_name, gl_entries_by_account, period_list):
	for entries in gl_entries_by_account.values():
		for entry in entries:

			d = accounts_by_name.get(entry.account)
			
			for period in period_list:
				# check if posting date is within the period
				if entry.posting_date <= period.to_date:
					d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)
					
def accumulate_values_into_parents(accounts, accounts_by_name, period_list):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = accounts_by_name[d.parent_account].get(period.key, 0.0) + \
					d.get(period.key, 0.0)


def prepare_data(accounts, balance_must_be, period_list):
	out = []

	for d in accounts:
		# add to output
		has_value = False
		row = {
			"account_name": d.account_name,
			"account": d.name,
			"parent_account": d.parent_account,
			"indent": flt(d.indent),
			"from_date": period_list[0]["from_date"],
			"to_date": period_list[-1]["to_date"]
		}

		for period in period_list:
			if d.get(period.key):
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= (1 if balance_must_be=="Debit" else -1)
			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if  abs(row[period.key]):
				# ignore zero values
				has_value = True

		if has_value:
			out.append(row)

	return out


def add_total_row(out, balance_must_be, period_list):
	row = {
		"account_name": "'" + _("Total ({0})").format(balance_must_be) + "'",
		"account": None
	}
	for period in period_list:
		row[period.key] = out[0].get(period.key, 0.0)
		out[0][period.key] = ""

	out.append(row)

	# blank row after Total
	out.append({})


def get_provisional_profit_loss(asset, liability, equity, period_list):
	if asset and (liability or equity):
		provisional_profit_loss = {
			"account_name": "'" + _("Provisional Profit / Loss (Credit)") + "'",
			"account": None,
			"warn_if_negative": True
		}

		has_value = False

		for period in period_list:
			effective_liability = 0.0
			if liability:
				effective_liability += flt(liability[-2][period.key])
				
			if equity:
				effective_liability += flt(equity[-2][period.key])

			provisional_profit_loss[period.key] = flt(asset[-2][period.key]) - effective_liability
			if provisional_profit_loss[period.key]:
				has_value = True

		if has_value:
			return provisional_profit_loss

def get_columns(period_list,period_list_last_year):
	
	columns = [{
		"fieldname": "account",
		"label": _("Account"),
		"fieldtype": "Link",
		"options": "Account",
		"width": 300
	}]
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"width": 150
		})
	for period in period_list_last_year:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"width": 150
		})
	columns.append({
		"fieldname": "diffrence",
		"label": _("Diffrence"),
		"fieldtype": "Currency",
		"width": 150
	})
	columns.append({
		"fieldname": "diffrence_percentage",
		"label": _("(%)Diffrence"),
		"fieldtype": "Percent",
		"width": 150
	})
	return columns


def get_result_as_list(data,data1,period_list,period_list_last_year):
	result = []

	for period in period_list_last_year:
		for period2 in period_list:
			for l in data:
				
				if any(d.get("account") == l.get("account") for d in data1):

					val=dict((d.get("account"),d) for d in data1) 
					l[period.key]= (val[l.get("account")]).get(period.key)

					list1=['Total (Debit)','Total (Credit)','Provisional Profit / Loss (Credit)']
					if l.get("account_name"):

						if l.get("account_name")[1:-1] in list1:
						
							for t in data1:

								if t.get("account_name"):

									if t.get("account_name")[1:-1] == l.get("account_name")[1:-1]:

										l[period.key]= t.get(period.key)
										l['diffrence'] = l.get(period2.key)-l.get(period.key)
										diff= (l.get("diffrence")/l.get(period.key))*100
										
										if diff:
											l['diffrence_percentage'] =diff
										
				if l.get("parent_account") and l.get(period2.key) and l.get(period.key):

					l['diffrence']	= (l.get(period2.key))- l.get(period.key)
			
	 				l['diffrence_percentage'] = (l.get("diffrence")/l.get(period.key))*100

	return data