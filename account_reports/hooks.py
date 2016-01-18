# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "account_reports"
app_title = "Account Reports"
app_publisher = "Indictrans"
app_description = "Accounting Reports"
app_icon = "octicon octicon-repo"
app_color = "#3498db"
app_email = "tejal.s@indictranstech.com"
app_version = "0.0.1"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/account_reports/css/account_reports.css"
# app_include_js = "/assets/account_reports/js/account_reports.js"

# include js, css files in header of web template
# web_include_css = "/assets/account_reports/css/account_reports.css"
# web_include_js = "/assets/account_reports/js/account_reports.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

fixtures = ['Custom Field', 'Property Setter']

# before_install = "account_reports.install.before_install"
# after_install = "account_reports.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "account_reports.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {

	"Sales Invoice": {
		"on_submit": [
			"erpnext.accounts.doctype.gst_details.gst_details.set_gst_details",
			"account_reports.account_reports.doctype.accounts_receivables_with_tax.accounts_receivables_with_tax.create_account_receivable_with_tax_entry"
		],
		"on_cancel": [
			"erpnext.accounts.doctype.gst_details.gst_details.del_cst_details_record",
			"account_reports.account_reports.doctype.accounts_receivables_with_tax.accounts_receivables_with_tax.delete_gl_entry"
		]

	},
	"Journal Entry": {
		"on_submit":"account_reports.account_reports.doctype.accounts_receivables_with_tax.accounts_receivables_with_tax.update_account_receivable_with_tax_entry",
		"on_cancel":"account_reports.account_reports.doctype.accounts_receivables_with_tax.accounts_receivables_with_tax.cancel_all_the_gl_entry"

	},
	"Purchase Invoice": {
		"on_submit": [
			"erpnext.accounts.doctype.gst_details.gst_details.set_gst_details_of_pi",
			"account_reports.account_reports.doctype.accounts_receivables_with_tax.accounts_receivables_with_tax.create_account_receivable_with_tax_entry"
		],
		"on_cancel": [
			"erpnext.accounts.doctype.gst_details.gst_details.del_cst_details_record",
			"account_reports.account_reports.doctype.accounts_receivables_with_tax.accounts_receivables_with_tax.delete_gl_entry"
		]

	},
	"Customer": {
		"validate": "erpnext.accounts.doctype.gst_details.gst_details.validate_cust_gst_type"			
	},
	"Supplier": {
		"validate": "erpnext.accounts.doctype.gst_details.gst_details.validate_supp_gst_type"			
	}

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"account_reports.tasks.all"
# 	],
# 	"daily": [
# 		"account_reports.tasks.daily"
# 	],
# 	"hourly": [
# 		"account_reports.tasks.hourly"
# 	],
# 	"weekly": [
# 		"account_reports.tasks.weekly"
# 	]
# 	"monthly": [
# 		"account_reports.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "account_reports.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "account_reports.event.get_events"
# }

