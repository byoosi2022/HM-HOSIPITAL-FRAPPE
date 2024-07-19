import frappe
from frappe import _
from frappe.utils import today, add_days
@frappe.whitelist()
def get_actual_qty(item_code, warehouse):
    actual_qty = frappe.db.get_value('Bin', {'item_code': item_code, 'warehouse': warehouse}, 'actual_qty')
    if actual_qty is None:
        actual_qty = 0
    return actual_qty

@frappe.whitelist()
def get_average_consumption(item_code, warehouse):
    end_date = today()
    start_date = add_days(end_date, -30)

    total_qty = frappe.db.sql("""
        SELECT SUM(actual_qty) 
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s 
        AND warehouse = %s 
        AND posting_date BETWEEN %s AND %s
        AND actual_qty < 0
    """, (item_code, warehouse, start_date, end_date))

    if total_qty and total_qty[0][0]:
        total_qty = abs(total_qty[0][0])
        average_consumption = total_qty
    else:
        average_consumption = 0

    return average_consumption

