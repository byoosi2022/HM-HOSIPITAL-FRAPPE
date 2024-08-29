import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_stock_entry(docname, warehouse, posting_date, posting_time, patient, cost_center):
    # Check if Stock Entry already exists
    stock_entry_list = frappe.get_list('Stock Entry', filters={'custom_pharmacy_id': docname, 'docstatus': 1}, fields=['name'])
    
    if stock_entry_list:
        return {'status': 'exists', 'message': 'Items already Issued Please'}
    
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
    se.custom_patient_id = patient
    se.custom_pharmacy_id = docname
    
    # Add Stock Entry details based on Medication Entry items
    for item in pharmacy.drug_prescription:
        item_code = item.drug_code
        item_doc = frappe.get_doc('Item', item_code)
        uom = item_doc.stock_uom  # Retrieve the UOM from the Item document
        
        # Check if the item has batch tracking enabled
        has_batch = frappe.get_value('Item', item_code, 'has_batch_no')
        
        if has_batch:
            # Get batch with available stock
            batch_info = frappe.get_list('Batch', filters={
                'item': item_code,
                'warehouse': warehouse,
                'actual_qty': ['>', 0]
            }, fields=['name'], limit=1)  # Get the first available batch
            
            if batch_info:
                batch_no = batch_info[0]['name']
            else:
                batch_no = None  # No available batch found
        else:
            batch_no = None  # No batch tracking for this item

        se.append('items', {
            'item_code': item_code,
            'qty': item.qty,
            'uom': uom,
            'transfer_qty': item.qty,
            'cost_center': cost_center,
            'batch_no': batch_no  # Set the batch number if available
        })
    
    se.insert()
    se.submit()
    return {'status': 'created', 'name': se.name}
