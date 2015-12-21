from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{	
			
			"label": _("Reports"),
			"icon": "icon-table",
			"items": [
				{
					"type": "report",
					"name": "Trial Balance C",
					"label": "Trial Balance",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Last Year Analysis",
					"label":"BS - Last Year Analysis",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Budget Analysis",
					"label": "Bs - Budget Analysis",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Balance Sheet",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name":"General Ledger Summary",
					"doctype": "GL Entry",
					"label":"General Ledger",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Profit and Loss Statement Reports",
					"label": "Profit and Loss Statement",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				# {
				# 	"type": "report",
				# 	"name": "GST Sales Details",
				# 	"label": "GST Sales Details",
				# 	"doctype": "GST Details",
				# 	"is_query_report": True
				# },
				# {
				# 	"type": "report",
				# 	"name": "GST Purchase Details",
				# 	"label": "GST Purchase Details",
				# 	"doctype": "GST Details",
				# 	"is_query_report": True
				# },
				{
					"type": "report",
					"name": "GST Details of Sales and Purchase",
					"label": "GST - Sales and Purchase Details",
					"doctype": "GST Details",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "GST Report",
					"label": "GST Report",
					"doctype": "GST Details",
					"is_query_report": True
				},
			]

				
		}

	]
