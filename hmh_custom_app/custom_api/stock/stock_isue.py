import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_stock_entry(docname, warehouse, posting_date, posting_time, patient, cost_center):
    # Check if Stock Entry already exists
    stock_entry_list = frappe.get_list('Stock Entry', filters={'custom_pharmacy_id': docname,'docstatus': 1}, fields=['name'])
    
    if stock_entry_list:
        return {'status': 'exists', 'message': 'Items already Isued Please'}
    
    # Fetch the Pharmacy document
    pharmacy = frappe.get_doc('Pharmacy', docname)
    
    if not pharmacy:
        return {'status': 'error', 'message': 'Pharmacy document not found'}
    
    # Create new Stock Entry
    se = frappe.new_doc('Stock Entry')
    se.stock_entry_type = 'Material Issue'
    se.from_warehouse = warehouse
    se.remarks = f"{patient} - {docname}"
    se.posting_date = posting_date
    se.posting_time = posting_time
    se.custom_paatient_id = patient
    se.custom_pharmacy_id = docname
    
    # Add Stock Entry details based on Medication Entry items
    for item in pharmacy.drug_prescription:
        item_code = item.drug_code
        item_doc = frappe.get_doc('Item', item_code)
        uom = item_doc.stock_uom  # Retrieve the UOM from the Item document
        
        se.append('items', {
            'item_code': item_code,
            'qty': item.qty,
            'uom': uom,
            'transfer_qty': item.qty,
            'cost_center': cost_center
        })
    
    se.insert()
    se.submit()
    return {'status': 'created', 'name': se.name}
