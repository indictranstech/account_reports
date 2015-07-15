# Copyright (c) 2013, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import (flt,cint,cstr, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)
import datetime
from frappe import _, _dict
from datetime import date
from time import strptime
from dateutil.relativedelta import relativedelta


@frappe.whitelist()
def get_month_details(fiscal_year,month):

	fy_start_end_date = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"])
	if not fy_start_end_date:
		frappe.throw(_("Fiscal Year {0} not found.").format(fiscal_year))

	current_year =((fy_start_end_date[0]).year)

	start_date = getdate(fy_start_end_date[0])
	end_date = getdate(fy_start_end_date[1])
	
	to_date = get_first_day(start_date)
	

	future_year= ((fy_start_end_date[1]).year)

	current_fiscal_year = cstr(cstr(current_year) +'-'+ cstr(future_year))

	last_fiscal_year =cstr(current_year-1) +'-'+ cstr(current_year)

	last_year= current_year - 1

	last_date_of_fiscal_year= start_date - datetime.timedelta(days=1)

	year_special_condition= ((last_date_of_fiscal_year).year)

	start_date_last_year= frappe.db.sql("""select year_start_date from `tabFiscal Year` where year_end_date='%s' """%last_date_of_fiscal_year,as_list=1)
	

	if month in ['Jan','Feb', 'Mar']:
		last_day_current_year= last_day_of_month(date(cint(fy_start_end_date[1].year), cint(strptime(month,'%b').tm_mon), cint(1)))
		last_day_last_year=last_day_of_month(date(cint(last_date_of_fiscal_year.year), cint(strptime(month,'%b').tm_mon), cint(1)))
		first_day = last_day_current_year + relativedelta(day=1)

	else:
	
		last_day_current_year= last_day_of_month(date(cint(current_year), cint(strptime(month,'%b').tm_mon), cint(1)))
		last_day_last_year=last_day_of_month(date(cint(last_year), cint(strptime(month,'%b').tm_mon), cint(1)))
		first_day = last_day_current_year + relativedelta(day=1)


	month_details ={'current_fiscal_year':current_fiscal_year,'last_fiscal_year':last_fiscal_year,
						'start_date_last_year':start_date_last_year,'end_date1':last_day_current_year,'last_year_to_date1':last_day_last_year,'start_date':start_date,'first_day':first_day
						} 

	return month_details

def last_day_of_month(any_day):
	next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  
	return next_month - datetime.timedelta(days=next_month.day)

	