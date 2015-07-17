# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import formatdate
import time
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import getdate
from account_reports.account_reports.utils import get_month_details
from frappe.utils import (flt,cint,cstr, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)
import datetime

def execute(filters=None):

	if not filters: filters = {}

	columns = get_columns(filters)

	period_month_ranges = get_period_month_ranges(filters["period"], filters["fiscal_year"],filters["company"])

	cam_map_income = get_costcenter_account_month_map_income(filters,'Income')

	cam_map_expense=get_costcenter_account_month_map_expense(filters,'Expense')

	cam_map_goods_sold = get_costcenter_account_month_map_goods_sold(filters,'Expense')
	
	data = []
	month_list=[]
	period_data = [0, 0, 0,0]

	row_first=[]

	abbr=frappe.db.get_value('Company', filters.get("company"), 'abbr')
	account= cstr('Cost of Goods Sold -' ) + cstr(' ') + cstr(abbr)


	if cam_map_income:
		row_first=get_income_details(columns,cam_map_income,period_month_ranges,month_list,data)
		if row_first:
			data.append(row_first)
	else:
		row_first=['Income', 0.0, 0.0, 0.0, '0%']
		data.append(row_first)

	if cam_map_goods_sold:
		row_second=get_cost_of_sales_details(columns,cam_map_goods_sold,period_month_ranges,month_list,data)
		if row_second:
			data.append(row_second)
	
		if row_first and row_second:
			row_third=get_gross_profit(row_first[1:],row_second[1:])
			if row_third:
				data.append(row_third)

	else:
		row_second=[account, 0.0, 0.0, 0.0, '0%']
		data.append(row_first)
		row_third=['Gross Profit',0.0,0.0,0.0,'0%']
		data.append(row_third)

	if cam_map_expense:
		row_fourth=get_expense_details(columns,cam_map_expense,period_month_ranges,month_list,data)
		if row_fourth:
			data.append(row_fourth)
		
		if row_first and row_fourth:
			row_fifth= get_net_profit_details(row_first[1:],row_fourth[1:])
			if row_fifth:
				data.append(row_fifth)

	else:
		row_fourth=['Expense', 0.0, 0.0, 0.0, '0%']
		data.append(row_fourth)
		row_fifth=['Net Profit/Loss',0.0,0.0,0.0,'0%']
		data.append(row_fifth)



	return columns,data


def get_income_details(columns,cam_map_income,period_month_ranges,month_list,data):
	month_list=[]
	for cost_center, cost_center_items in cam_map_income.items():
		for account, monthwise_data in cost_center_items.items():
			row = [cost_center]
			totals = [0, 0, 0,0]
			
			for relevant_months in period_month_ranges:
				period_data = [0, 0, 0,0]
				for month in relevant_months:
					month_data = monthwise_data.get(month, {})
					month_list.append(month_data)

	total_target= sum([month.get('target') for month in month_list])
	total_actual= sum([month.get('actual') for month in month_list])
	row=get_variance_and_percentage(columns,cam_map_income,period_month_ranges,month_list,data,period_data,row,total_actual,total_target)
	return row
	
def get_cost_of_sales_details(columns,cam_map_goods_sold,period_month_ranges,month_list,data):
	month_list=[]
	for cost_center, cost_center_items in cam_map_goods_sold.items():
		for account, monthwise_data in cost_center_items.items():
			row = [account]
			totals = [0, 0, 0,0]
			
			for relevant_months in period_month_ranges:
				period_data = [0, 0, 0,0]
				for month in relevant_months:
					month_data = monthwise_data.get(month, {})
					month_list.append(month_data)
			
	
	total_target= sum([month.get('target') for month in month_list])

	total_actual= sum([month.get('actual') for month in month_list])
	row=get_variance_and_percentage(columns,cam_map_goods_sold,period_month_ranges,month_list,data,period_data,row,total_actual,total_target)
	return row
	

def get_expense_details(columns,cam_map_expense,period_month_ranges,month_list,data):
	month_list=[]
	for cost_center, cost_center_items in cam_map_expense.items():
		for account, monthwise_data in cost_center_items.items():
			row = [cost_center]
			totals = [0, 0, 0,0]
			
			for relevant_months in period_month_ranges:
				period_data = [0, 0, 0,0]
				for month in relevant_months:
					month_data = monthwise_data.get(month, {})
					month_list.append(month_data)
	
	total_target= sum([month.get('target') for month in month_list])
	total_actual= sum([month.get('actual') for month in month_list])

	row=get_variance_and_percentage(columns,cam_map_expense,period_month_ranges,month_list,data,period_data,row,total_actual,total_target)
	
	return row

def get_variance_and_percentage(columns,cam_map_income,period_month_ranges,month_list,data,period_data,row,total_actual,total_target):
	
	for j,fieldname in enumerate(["target", "actual", "variance","diffrence"]):
		if j==0:
			period_data[j] += total_target
		elif j==1:
			period_data[j] += total_actual

	if period_data[0]>0 and period_data[1]==0:
		period_data[2] = period_data[0] - period_data[1]

		if period_data[2]==0:
			period_data[3]=cstr('0%')
		else:
			period_data[3] = cstr(round(flt((period_data[2]/period_data[0])*100),2)) + cstr('%')
		row += period_data
	
	elif period_data[0]==0 and period_data[1]>0:
		period_data[2] = (period_data[0] - period_data[1])*(-1)
		if period_data[2]==0:
			period_data[3]=cstr('0%')
		else:
			period_data[3] = 'NA'

		row += period_data
		
	elif period_data[0]==0 and period_data[1]==0:
		period_data[2] = 0
		period_data[3]=cstr('0%')
		row += period_data

	elif period_data[0]>0 and period_data[1]>0:
		period_data[2] = period_data[0] - period_data[1]
		if period_data[2]==0:
			period_data[3]=0
		else:
			period_data[3] = cstr(round(flt((period_data[2]/period_data[0])*100),2)) + cstr('%')

		row += period_data

	elif period_data[0]>0 and period_data[1]<0:
		period_data[2] = period_data[0] - period_data[1]
		period_data[3] = cstr(round(flt((period_data[2]/period_data[0])*100),2)) + cstr('%')
		row += period_data

	elif period_data[0]==0 and period_data[1]<0:
		period_data[2] = period_data[0] - period_data[1]
		period_data[3]='NA'
		#period_data[3] = cstr(round(flt((period_data[2]/period_data[0])*100),2)) + cstr('%')
		row += period_data

	return row


def get_gross_profit(first,second):
	row = ['Gross Profit']
	period_data =[0,0,0,0]
	period_data=[flt(x) - flt(y) for x, y in zip(first, second)]
	row+=period_data
	return row
	
def get_net_profit_details(first,fourth):
	row = ['Net Profit/Loss']
	period_data =[0,0,0,0]
	period_data=[flt(x) - flt(y) for x, y in zip(first, fourth)]
	row+=period_data
	return row	

def get_period_month_ranges(period, fiscal_year,company):

	from dateutil.relativedelta import relativedelta
	period_month_ranges = []

	for start_date, end_date in get_period_date_ranges(period, fiscal_year,company):
		months_in_this_period = []
		while start_date <= end_date:
			months_in_this_period.append(start_date.strftime("%B"))

			start_date += relativedelta(months=1)
		period_month_ranges.append(months_in_this_period)

	return period_month_ranges

def get_period_date_ranges(period, fiscal_year=None,company=None, year_start_date=None):
	
	month_details= get_month_details(fiscal_year,period)

	period_date_ranges = []
	
	period_date_ranges.append([month_details.get('first_day'),month_details.get('end_date1')])

	return period_date_ranges

def get_columns(filters):

	for fieldname in ["fiscal_year", "period", "company"]:
		if not filters.get(fieldname):
			label = (" ".join(fieldname.split("_"))).title()
			msgprint(_("Please specify") + ": " + label,
				raise_exception=True)

	columns = [ _("Account") + ":Data:120"]

	
	for from_date, to_date in get_period_date_ranges(filters["period"], filters["fiscal_year"]):
		for label in [_("Budgeted") + " (%s)", _("Selected Period") + " (%s)", _("Diffrence") + " (%s)"]:
			label = label % formatdate(from_date, format_string="MMM")
			
			columns.append(label+":Float:150")
		columns.append(_("Diffrence Percentage") + ":Data:120")

	return columns 


#Get cost center & target details
def get_costcenter_target_details(filters,root_type):

	cost_center_details= frappe.db.sql("""select cc.name, cc.distribution_id,
		cc.parent_cost_center, bd.account, bd.budget_allocated,bd.root_type
		from `tabCost Center` cc, `tabBudget Detail` bd
		where bd.parent=cc.name and bd.fiscal_year=%s and bd.root_type=%s and
		cc.company=%s order by cc.name""" % ('%s', '%s' ,'%s'),
		(filters.get("fiscal_year"), root_type, filters.get("company")), as_dict=1)

	return cost_center_details


#Get target distribution details of accounts of cost center
def get_target_distribution_details(filters):
	target_details = {}

	for d in frappe.db.sql("""select md.name, mdp.month, mdp.percentage_allocation
		from `tabMonthly Distribution Percentage` mdp, `tabMonthly Distribution` md
		where mdp.parent=md.name and md.fiscal_year=%s""", (filters["fiscal_year"]),as_dict=1):
			target_details.setdefault(d.name, {}).setdefault(d.month, flt(d.percentage_allocation))
	
	return target_details


#Get actual details from gl entry
def get_actual_details(filters):
	ac_details = frappe.db.sql("""select gl.account, gl.debit, gl.credit,
		gl.cost_center, MONTHNAME(gl.posting_date) as month_name
		from `tabGL Entry` gl, `tabBudget Detail` bd
		where gl.fiscal_year=%s and company=%s
		and bd.account=gl.account and bd.parent=gl.cost_center""" % ('%s', '%s'),
		(filters.get("fiscal_year"), filters.get("company")), as_dict=1)

	cc_actual_details = {}
	for d in ac_details:
		cc_actual_details.setdefault(d.cost_center, {}).setdefault(d.account, []).append(d)

	return cc_actual_details
	

def get_costcenter_account_month_map_income(filters,root_type):
	cam_map_income=get_data_for_income(filters,root_type)

	return cam_map_income

def get_costcenter_account_month_map_expense(filters,root_type):
	cam_map_expense=get_data_for_expense(filters,root_type)

	return cam_map_expense

def get_costcenter_account_month_map_goods_sold(filters,root_type):
	cam_map_goods_sold=get_data_for_goods_sold(filters,root_type)

	return cam_map_goods_sold

def get_data_for_income(filters,root_type):

	costcenter_target_details = get_costcenter_target_details(filters,root_type)
	tdd = get_target_distribution_details(filters)
	actual_details = get_actual_details(filters)

	cam_map_income = {}

	for ccd in costcenter_target_details:
		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime('%B')
			cam_map_income.setdefault('Income', {}).setdefault(ccd.account, {})\
				.setdefault(month, frappe._dict({
					"target": 0.0, "actual": 0.0
				}))

			tav_dict = cam_map_income['Income'][ccd.account][month]
			month_percentage = tdd.get(ccd.distribution_id, {}).get(month, 0) \
				if ccd.distribution_id else 100.0/12
			tav_dict.target += flt(ccd.budget_allocated) * month_percentage / 100

			for ad in actual_details.get(ccd.name, {}).get(ccd.account, []):
				if ad.month_name == month:
						tav_dict.actual += flt(ad.debit) - flt(ad.credit)

	return cam_map_income


def get_data_for_expense(filters,root_type):
	costcenter_target_details = get_costcenter_target_details(filters,root_type)
	tdd = get_target_distribution_details(filters)
	actual_details = get_actual_details(filters)
	cam_map_expense = {}

	for ccd in costcenter_target_details:
		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime('%B')
			cam_map_expense.setdefault('Expense', {}).setdefault(ccd.account, {})\
				.setdefault(month, frappe._dict({
					"target": 0.0, "actual": 0.0
				}))

			tav_dict = cam_map_expense['Expense'][ccd.account][month]
			month_percentage = tdd.get(ccd.distribution_id, {}).get(month, 0) \
				if ccd.distribution_id else 100.0/12
			tav_dict.target+= flt(ccd.budget_allocated) * month_percentage / 100
			for ad in actual_details.get(ccd.name, {}).get(ccd.account, []):
				if ad.month_name == month:
						tav_dict.actual += flt(ad.debit) - flt(ad.credit)

	return cam_map_expense



def get_data_for_goods_sold(filters,root_type):
	abbr=frappe.db.get_value('Company', filters.get("company"), 'abbr')
	account= cstr('Cost of Goods Sold -' ) + cstr(' ') + cstr(abbr)
	cost_center_details= frappe.db.sql("""select cc.name, cc.distribution_id,
		cc.parent_cost_center, bd.account, bd.budget_allocated,bd.root_type
		from `tabCost Center` cc, `tabBudget Detail` bd
		where bd.parent=cc.name and bd.fiscal_year=%s and bd.root_type=%s and bd.account=%s and
		cc.company=%s order by cc.name""" % ('%s', '%s' ,'%s','%s'),
		(filters.get("fiscal_year"), root_type,account, filters.get("company")), as_dict=1)

	tdd = get_target_distribution_details(filters)
	actual_details = get_actual_details(filters)
	cam_map_goods_sold = {}

	for ccd in cost_center_details:
		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime('%B')
			cam_map_goods_sold.setdefault(ccd.name, {}).setdefault(ccd.account, {})\
				.setdefault(month, frappe._dict({
					"target": 0.0, "actual": 0.0
				}))

			tav_dict = cam_map_goods_sold[ccd.name][ccd.account][month]
			month_percentage = tdd.get(ccd.distribution_id, {}).get(month, 0) \
				if ccd.distribution_id else 100.0/12

			tav_dict.target += flt(ccd.budget_allocated) * month_percentage / 100
			for ad in actual_details.get(ccd.name, {}).get(ccd.account, []):
				if ad.month_name == month:
						tav_dict.actual += flt(ad.debit) - flt(ad.credit)

	return cam_map_goods_sold
