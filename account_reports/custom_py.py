# import frappe

# @frappe.whitelist()
# def fetch_taxes(item):
# 	tax_list=[]
# 	item_code=frappe.get_doc("Item",item)
# 	for row in item_code.get("taxes"):
# 		tax_code=row.tax_code
# 		tax_type=row.tax_type
# 		tax_rate=row.tax_rate
# 		tax= {"tax_code":tax_code, "tax_type":tax_type, "tax_rate":tax_rate}
# 		tax_list.append(tax)
# 	return tax_list


