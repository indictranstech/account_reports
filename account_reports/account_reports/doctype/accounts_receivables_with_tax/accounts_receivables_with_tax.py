# -*- coding: utf-8 -*-
# Copyright (c) 2015, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cint, cstr, date_diff, rounded, flt, getdate, nowdate, \
	get_first_day, get_last_day,money_in_words, now, nowtime

class AccountsReceivablesWithTax(Document):
	pass
	
def create_account_receivable_with_tax_entry(doc,method):

	if doc.doctype == 'Sales Invoice':
		sales_tax=frappe.db.sql(""" select name from `tabSales Taxes and Charges` where
							parent='%s'"""%doc.name,as_list=1)
	elif doc.doctype=='Purchase Invoice':

		sales_tax=frappe.db.sql(""" select name from `tabPurchase Taxes and Charges` where
							parent='%s'"""%doc.name,as_list=1)

	if len(sales_tax)>0:
		if doc:
			create_account_gl_entry_for_amount(doc,method)
			for i in sales_tax:
				make_tax_entry(doc,i[0],method)
	else:
		create_account_gl_entry_for_amount(doc,method)
		frappe.db.sql("""update `tabAccounts Receivables With Tax` set outstanding_tax_amount='%s' where voucher_no='%s'"""%(0.0,doc.name))
		frappe.db.commit()

def create_account_gl_entry_for_amount(doc,method):
	with_tax = frappe.new_doc('Accounts Receivables With Tax')
	with_tax.posting_date = nowdate()
	with_tax.transaction_date = nowdate()
	
	if doc.doctype == 'Sales Invoice':
		with_tax.account = doc.debit_to
		with_tax.party_type= 'Customer'
		with_tax.against_voucher_type= 'Sales Invoice'
		with_tax.voucher_type= 'Sales Invoice'
		with_tax.party=doc.customer
		with_tax.credit=0.0
		with_tax.debit= doc.grand_total
		with_tax.against= doc.against_income_account

	elif doc.doctype == 'Purchase Invoice':

		with_tax.account = doc.credit_to
		with_tax.party_type= 'Supplier'
		with_tax.against_voucher_type= 'Purchase Invoice'
		with_tax.voucher_type= 'Purchase Invoice'
		with_tax.party=doc.supplier
		with_tax.debit=0.0
		with_tax.credit= doc.grand_total
		with_tax.against= doc.credit_to
	
	with_tax.against_voucher= doc.name
	with_tax.voucher_no = doc.name
	with_tax.paid_amount = doc.grand_total-doc.outstanding_amount
	with_tax.outstanding_amount= doc.outstanding_amount
	with_tax.is_opening=doc.is_opening
	with_tax.fiscal_year=doc.fiscal_year
	with_tax.company= doc.company
	with_tax.save(ignore_permissions=True)
	

def make_tax_entry(doc,i,method):

	if doc.doctype == 'Sales Invoice':
		tax_details= frappe.db.sql("""select account_head,cost_center,tax_amount_after_discount_amount
		  							from `tabSales Taxes and Charges` where name='%s'"""%i,as_list=1)

	elif doc.doctype == 'Purchase Invoice':
		tax_details= frappe.db.sql("""select account_head,cost_center,tax_amount_after_discount_amount
		  							from `tabPurchase Taxes and Charges` where name='%s'"""%i,as_list=1)

	if tax_details:
		gl_entry= frappe.new_doc('Accounts Receivables With Tax')
		gl_entry.posting_date = nowdate()
		gl_entry.transaction_date = nowdate()
		gl_entry.account = tax_details[0][0]

		if doc.doctype == 'Sales Invoice':

			gl_entry.party_type= 'Customer'
			gl_entry.party=doc.customer
			gl_entry.against_voucher_type= 'Sales Invoice'
			gl_entry.against= doc.debit_to
			gl_entry.voucher_type= 'Sales Invoice'
			gl_entry.credit=tax_details[0][2]
			gl_entry.debit= 0.0

		elif doc.doctype == 'Purchase Invoice':

			gl_entry.party_type= 'Supplier'
			gl_entry.party=doc.supplier
			gl_entry.against_voucher_type= 'Purchase Invoice'
			gl_entry.voucher_type= 'Purchase Invoice'
			gl_entry.debit=tax_details[0][2]
			gl_entry.credit= 0.0
			gl_entry.against= doc.credit_to

		
		gl_entry.cost_center= tax_details[0][1]
		gl_entry.against_voucher= doc.name
		gl_entry.voucher_no = doc.name
		gl_entry.outstanding_amount= doc.outstanding_amount
		gl_entry.paid_tax_amount = 0.00
		gl_entry.outstanding_tax_amount= tax_details[0][2]
		gl_entry.is_opening=doc.is_opening
		gl_entry.fiscal_year=doc.fiscal_year
		gl_entry.company= doc.company
		gl_entry.save(ignore_permissions=True)

#########Sales Invoice Cancel############################################################################

def delete_gl_entry(doc,method):
	if doc.doctype=='Sales Invoice':
		voucher_type='Sales Invoice'
		delete_entry(voucher_type,doc.name)
	elif doc.doctype=='Purchase Invoice':
		voucher_type='Purchase Invoice'
		delete_entry(voucher_type,doc.name)

def delete_entry(voucher_type,name):
	gl_entry= frappe.db.sql("""select name from `tabAccounts Receivables With Tax` where voucher_no='%s'
		and voucher_type='%s'"""%(name,voucher_type),as_list=1)
	if gl_entry:
		if len(gl_entry)>0:
			for i in gl_entry:
				frappe.db.sql("""delete from `tabAccounts Receivables With Tax` where name='%s'"""%(i[0]))
				frappe.db.commit()

#####JV################################################################################################################################
def update_account_receivable_with_tax_entry(doc,method):
	#frappe.errprint(doc)
	if doc:
		test,ledger_entries=get_general_account_entries(doc,method)
		if 'True' in test:
			get_credit_debit_details(doc,method,test,ledger_entries)

def get_general_account_entries(doc,method):
	ledger_entries= frappe.db.sql("""select name from `tabJournal Entry Account` where
									parent ='%s'"""%doc.name,as_list=1)

	test =[]

	if len(ledger_entries)> 0:

		for i in ledger_entries:
			against_invoice = frappe .db.get_value("Journal Entry Account",i[0],'against_invoice')
			against_voucher = frappe .db.get_value("Journal Entry Account",i[0],'against_voucher')
			if against_invoice:
				test.append('True')
				test.append(against_invoice)
				test.append('Sales Invoice')
			elif against_voucher:
				test.append('True')
				test.append(against_voucher)
				test.append('Purchase Invoice')

	return test , ledger_entries


def get_credit_debit_details(doc,method,test,ledger_entries):
	outstanding_amount=[]
	if test[2] == 'Sales Invoice':
		outstanding_amount= frappe.db.sql("""select ifnull(outstanding_amount,0),ifnull(grand_total,0),ifnull(total,0) from `tabSales Invoice` where name ='%s' """%test[1],as_list=1)

	elif test[2] =='Purchase Invoice':
		outstanding_amount= frappe.db.sql("""select ifnull(outstanding_amount,0),ifnull(grand_total,0),ifnull(total,0) from `tabPurchase Invoice` where name ='%s' """%test[1],as_list=1)

	
	if outstanding_amount>0:
		if outstanding_amount[0][0] == outstanding_amount[0][1] and outstanding_amount[0][0] == doc.total_debit:
			gl_entry_name= frappe.db.sql("""select name from `tabAccounts Receivables With Tax` where voucher_no='%s' """%test[1],as_list=1)
			if gl_entry_name:
				for gl in gl_entry_name:
					update_all_gl_entries(gl[0],outstanding_amount)
		else:
			for j in ledger_entries:
				account= frappe.db.sql("""select account from `tabJournal Entry Account` where parent='%s' and account!='Debtors - F'"""%doc.name,as_list=1)
				ledger_details=frappe.db.sql("""select account, ifnull(debit,0) , ifnull(credit,0) ,ifnull(against_invoice,0)
												from `tabJournal Entry Account` where name = '%s'"""%j[0],as_list=1)
				if test[2] == 'Sales Invoice':
					outstanding_amount= frappe.db.sql("""select ifnull(outstanding_amount,0),ifnull(grand_total,0),ifnull(total,0) from `tabSales Invoice` where name ='%s' """%test[1],as_list=1)

				elif test[2] == 'Purchase Invoice':
					outstanding_amount= frappe.db.sql("""select ifnull(outstanding_amount,0),ifnull(grand_total,0),ifnull(total,0) from `tabPurchase Invoice` where name ='%s' """%test[1],as_list=1)

				if ledger_details[0][0] == 'Debtors - F' or ledger_details[0][0] == 'Creditors - F':
					
					check_entry_is_available_in_gl_entry(ledger_details,test[1],outstanding_amount[0][0],test,account)
					
				else:
					gl_entry_tax=check_account_is_taxaccount(ledger_details,test[1],outstanding_amount[0][0],test)
					
					if gl_entry_tax:
						update_gl_tax_entry(gl_entry_tax,ledger_details,test)
					else:
					 	pass
		

def check_account_is_taxaccount(ledger_details,sales_invoice,outstanding_amount,test):

	if test[2] == 'Sales Invoice':
		account_head= frappe.db.sql("""select account_head from `tabSales Taxes and Charges` where parent='%s'"""%sales_invoice,as_list=1)

	elif test[2] == 'Purchase Invoice':
		account_head= frappe.db.sql("""select account_head from `tabPurchase Taxes and Charges` where parent='%s'"""%sales_invoice,as_list=1)

	if len(account_head)>0:
		for i in account_head:
			if ledger_details[0][0]==i[0]:
				gl_entry_tax=check_entry_is_available_in_gl_for_tax(ledger_details,sales_invoice,outstanding_amount,test)
				if gl_entry_tax:
					return gl_entry_tax
				

def check_entry_is_available_in_gl_for_tax(ledger_details,sales_invoice,outstanding_amount,test):

	gl_entry_tax= frappe.db.sql("""select name,ifnull(outstanding_amount,0), ifnull(outstanding_tax_amount,0) from `tabAccounts Receivables With Tax` 
		where voucher_no='%s' and account='%s' and outstanding_tax_amount>0"""%(sales_invoice,ledger_details[0][0]),as_list=1)
	
	if gl_entry_tax:

		return gl_entry_tax

def update_gl_tax_entry(gl_entry_tax,ledger_details,test):
		if test[2] == 'Sales Invoice':

			if gl_entry_tax[0][2]==ledger_details[0][1]:
				outstanding_tax_amount=gl_entry_tax[0][2] - ledger_details[0][1]
				debit= ledger_details[0][1]
				paid_tax_amount=ledger_details[0][1]
				total_outstanding_amount=gl_entry_tax[0][1] - ledger_details[0][1]	

			elif gl_entry_tax[0][2]>ledger_details[0][1]:
				paid_tax_amount=ledger_details[0][1]
				outstanding_tax_amount=gl_entry_tax[0][2] - ledger_details[0][1]
				debit= ledger_details[0][1]
				total_outstanding_amount = gl_entry_tax[0][1]-ledger_details[0][1]
			
			elif gl_entry_tax[0][2] < ledger_details[0][1]:
				paid_tax_amount=gl_entry_tax[0][2]
				outstanding_tax_amount=0.0
				debit=gl_entry_tax[0][2]
				total_outstanding_amount=gl_entry_tax[0][1] - gl_entry_tax[0][2]

			update_gl_entry_for_tax(outstanding_tax_amount,debit,paid_tax_amount,gl_entry_tax,total_outstanding_amount,test)

		elif test[2] == 'Purchase Invoice':

			if gl_entry_tax[0][2]==ledger_details[0][2]:
				outstanding_tax_amount=gl_entry_tax[0][2] - ledger_details[0][2]
				credit= ledger_details[0][2]
				paid_tax_amount=ledger_details[0][2]
				total_outstanding_amount=gl_entry_tax[0][1] - ledger_details[0][2]	

			elif gl_entry_tax[0][2]>ledger_details[0][2]:
				paid_tax_amount=ledger_details[0][2]
				outstanding_tax_amount=gl_entry_tax[0][2] - ledger_details[0][2]
				credit= ledger_details[0][2]
				total_outstanding_amount = gl_entry_tax[0][1]-ledger_details[0][2]
			
			elif gl_entry_tax[0][2] < ledger_details[0][2]:
				paid_tax_amount=gl_entry_tax[0][2]
				outstanding_tax_amount=0.0
				credit=gl_entry_tax[0][2]
				total_outstanding_amount=gl_entry_tax[0][1] - gl_entry_tax[0][2]

			update_gl_entry_for_tax(outstanding_tax_amount,credit,paid_tax_amount,gl_entry_tax,total_outstanding_amount,test)

def  check_entry_is_available_in_gl_entry(ledger_details,sales_invoice,outstanding_amount,test,account):
	gl_entry_name= frappe.db.sql("""select name from `tabAccounts Receivables With Tax` where voucher_no='%s' and account='%s' and outstanding_amount>0"""%(sales_invoice,ledger_details[0][0]),as_list=1)

	if len(gl_entry_name)>0:
		for i in gl_entry_name:

			gl_entry= frappe.db.sql("""select ifnull(outstanding_amount,0) from `tabAccounts Receivables With Tax` where voucher_no='%s'
									and account='%s' and outstanding_amount>0 and name ='%s'"""%(sales_invoice,ledger_details[0][0],i[0]),as_list=1)
			if gl_entry and test[2]=='Sales Invoice':
				if ledger_details[0][2] >0 :
					credit,paid_amount,total_outstanding_amount=calculate_the_outstanding_tax_credit(gl_entry[0][0],ledger_details[0][2],test)
					update_gl_entry(credit,paid_amount,total_outstanding_amount,i[0],test)
					update_outstanding_amount(i[0],total_outstanding_amount,sales_invoice,test,account)
				else:
					credit,paid_amount,total_outstanding_amount=calculate_the_outstanding_tax_credit(gl_entry[0][0],ledger_details[0][1],test)
					update_gl_entry(credit,paid_amount,total_outstanding_amount,i[0],test)

			elif gl_entry and test[2] == 'Purchase Invoice':
				if ledger_details[0][2] >0 :
					debit,paid_amount,total_outstanding_amount=calculate_the_outstanding_tax_debit(gl_entry[0][0],ledger_details[0][2],test)
					update_gl_entry(debit,paid_amount,total_outstanding_amount,i[0],test)

				else:
					debit,paid_amount,total_outstanding_amount=calculate_the_outstanding_tax_debit(gl_entry[0][0],ledger_details[0][1],test)
					update_gl_entry(debit,paid_amount,total_outstanding_amount,i[0],test)
					update_outstanding_amount(i[0],total_outstanding_amount,sales_invoice,test,account)


def calculate_the_outstanding_tax_credit(amount,credit,test):

	if amount==credit:
		total_outstanding_amount= 0.0
		credit=credit
		paid_amount=credit

	elif amount>credit:
		paid_amount=credit
		credit= credit
		total_outstanding_amount = amount-credit
	
	elif amount < credit:
		paid_amount= amount
		credit=amount
		total_outstanding_amount=0.0

	return credit,paid_amount,total_outstanding_amount

def calculate_the_outstanding_tax_debit(amount,debit,test):

	if amount==debit:
		total_outstanding_amount= 0.0
		debit=debit
		paid_amount=credit

	elif amount>debit:
		paid_amount=debit
		debit=debit
		total_outstanding_amount = amount-debit
	
	elif amount < debit:
		paid_amount= amount
		debit=amount
		total_outstanding_amount=0.0

	return debit,paid_amount,total_outstanding_amount


def update_gl_entry(credit,paid_amount,total_outstanding_amount,gl_entry,test):
	gl = frappe.get_doc('Accounts Receivables With Tax', gl_entry)

	if test[2]=='Sales Invoice':
		gl.credit=credit

	elif test[2]=='Purchase Invoice':
		gl.debit = credit

	gl.paid_amount=paid_amount
	gl.outstanding_amount=total_outstanding_amount
	gl.save(ignore_permissions=True)

def update_outstanding_amount(gl_entry,outstanding_amount,sales_invoice,test,account):
	if test[2]=='Sales Invoice':

		gl_entry= frappe.db.sql("""select name from `tabAccounts Receivables With Tax` where voucher_no='%s' and account!='Debtors - F' and account!='%s' """%(sales_invoice,account[0][0]),as_list=1)
	elif test[2]=='Purchase Invoice':
		gl_entry= frappe.db.sql("""select name from `tabAccounts Receivables With Tax` where voucher_no='%s' and account!='Creditors - F' and account!='%s'"""%(sales_invoice,account[0][0]),as_list=1)

	if gl_entry:
		for i in gl_entry:
			gl = frappe.get_doc('Accounts Receivables With Tax', i[0])
			gl.outstanding_amount=outstanding_amount
			gl.save(ignore_permissions=True)

def update_gl_entry_for_tax(outstanding_tax_amount,debit,paid_tax_amount,gl_entry_tax,total_outstanding_amount,test):
	gl_tax = frappe.get_doc('Accounts Receivables With Tax', gl_entry_tax[0][0])

	if test[2] == 'Sales invoice':
		gl_tax.debit=debit

	elif test[2] == 'Purchase Invoice':
		gl_tax.credit=debit

	gl_tax.paid_tax_amount=paid_tax_amount
	gl_tax.outstanding_amount=total_outstanding_amount
	gl_tax.outstanding_tax_amount=outstanding_tax_amount
	gl_tax.save(ignore_permissions=True)
	
def update_all_gl_entries(name,outstanding_amount):
	gl_name = frappe.get_doc('Accounts Receivables With Tax', name)
	gl_name.outstanding_amount=0.0
	gl_name.outstanding_tax_amount=0.0
	gl_name.save(ignore_permissions=True)


#Jv Cancel ##############################################################################################

def cancel_all_the_gl_entry(doc,method):

	test,ledger_entries=get_general_account_entries(doc,method)
	if 'True' in test:
		for j in ledger_entries:
			account= frappe.db.sql("""select account from `tabJournal Entry Account` where parent='%s' and account!='Debtors - F'"""%doc.name,as_list=1)
			ledger_details=frappe.db.sql("""select account, ifnull(debit,0) , ifnull(credit,0) ,ifnull(against_invoice,0)
											from `tabJournal Entry Account` where name = '%s'"""%j[0],as_list=1)
			if ledger_details[0][0] == 'Debtors - F' or ledger_details[0][0] == 'Creditors - F':

				gl_entry_name= frappe.db.sql("""select name,ifnull(outstanding_amount,0) from `tabAccounts Receivables With Tax` where voucher_no='%s' and account='%s'"""%(test[1],ledger_details[0][0]),as_list=1)
				update_gl_entry_for_debetors(gl_entry_name,ledger_details)
				update_tax_entry_outstanding_amount(ledger_details,test,account)
			else:
				gl_entry_for_tax= frappe.db.sql("""select name ,ifnull(outstanding_amount,0), ifnull(outstanding_tax_amount,0),ifnull(paid_tax_amount,0),account from `tabAccounts Receivables With Tax` where voucher_no='%s' and account='%s'"""%(test[1],ledger_details[0][0]),as_list=1)
				if gl_entry_for_tax:
					update_gl_entry_for_tax_on_cancel(gl_entry_for_tax,ledger_details,test)

def update_gl_entry_for_debetors(gl_entry_name,ledger_details):
	if ledger_details[0][1]>0:
		gl = frappe.get_doc('Accounts Receivables With Tax', gl_entry_name[0][0])
		gl.outstanding_amount = gl_entry_name[0][1] + ledger_details[0][1]
		gl.save(ignore_permissions=True)
	elif ledger_details[0][2]>0:
		gl = frappe.get_doc('Accounts Receivables With Tax', gl_entry_name[0][0])
		gl.outstanding_amount = gl_entry_name[0][1] + ledger_details[0][2]
		gl.save(ignore_permissions=True)


def update_tax_entry_outstanding_amount(ledger_details,test,account):
	if test[2]=='Sales Invoice':

		gl_entry_tax=frappe.db.sql("""select name,ifnull(outstanding_amount,0),ifnull(paid_tax_amount,0),ifnull(outstanding_tax_amount,0) from `tabAccounts Receivables With Tax` where voucher_no='%s' and account!='Debtors - F' and account!='%s'"""%(test[1],account[0][0]),as_list=1)

	elif test[2]=='Purchase Invoice':
		gl_entry_tax=frappe.db.sql("""select name,ifnull(outstanding_amount,0),ifnull(paid_tax_amount,0),ifnull(outstanding_tax_amount,0) from `tabAccounts Receivables With Tax` where voucher_no='%s' and account!='Debtors - F' and account!='%s'"""%(test[1],account[0][0]),as_list=1)

	if len(gl_entry_tax)>0:
		for i in gl_entry_tax:
			gl_tax = frappe.get_doc('Accounts Receivables With Tax', i[0])

			if ledger_details[0][1]>0:
				gl_tax.outstanding_amount= gl_entry_tax[0][1] + ledger_details[0][1]
			elif ledger_details[0][2]>0:
				gl_tax.outstanding_amount= gl_entry_tax[0][1] + ledger_details[0][2]
				
			gl_tax.save(ignore_permissions=True)

def update_gl_entry_for_tax_on_cancel(gl_entry_for_tax,ledger_details,test):
	gl_tax = frappe.get_doc('Accounts Receivables With Tax', gl_entry_for_tax[0][0])
	if test[2]=='Sales Invoice':
		gl_tax.outstanding_amount = gl_entry_for_tax[0][1] + ledger_details[0][1]
		gl_tax.outstanding_tax_amount=gl_entry_for_tax[0][3] + ledger_details[0][1]

	elif test[2] == 'Purchase Invoice':
		gl_tax.outstanding_amount = gl_entry_for_tax[0][1] + ledger_details[0][2]
		gl_tax.outstanding_tax_amount=gl_entry_for_tax[0][2] + ledger_details[0][2]
	gl_tax.save(ignore_permissions=True)

	


	



