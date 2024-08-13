import frappe
from frappe import _

def on_submit(doc, method):
    # Check if payment_status is already set; if so, exit the function
    if doc.payment_status:
        return
    
    if doc.patient:
        try:
            # Fetch the Patient document
            patient_doc = frappe.get_doc('Patient', doc.patient)
            customer = frappe.get_doc('Customer', patient_doc.customer)
            
            # Get the default receivable account from Company
            receivable_account = frappe.get_value('Company', doc.company, 'default_receivable_account')
            
            # If not found, get it from the Customer Group
            if not receivable_account:
                customer_group = frappe.get_doc('Customer Group', customer.customer_group)
                if customer_group.accounts:
                    for default in customer_group.accounts:
                        if default.account:
                            receivable_account = default.account
                            break
            
            if not receivable_account:
                frappe.throw(_("Default Receivable Account is not set for the company {0} or the customer group {1}").format(doc.company, customer.customer_group))
            
            # Check if there is an existing draft Sales Invoice for the same encounter
            existing_invoice = frappe.get_all("Sales Invoice", 
                                              filters={
                                                  "custom_pharmacy_id": doc.name,
                                                  "docstatus": 0  # Draft status
                                              }, 
                                              limit=1)
            
            if existing_invoice:
                # Update the existing draft Sales Invoice
                sales_invoice = frappe.get_doc("Sales Invoice", existing_invoice[0].name)
                sales_invoice.set_posting_time = 1
                sales_invoice.cost_center = doc.medical_department
                sales_invoice.posting_date = doc.encounter_date
                
                # Handle None values for due_date
                encounter_date = doc.encounter_date or frappe.utils.nowdate()
                sales_invoice.due_date = encounter_date
                
                sales_invoice.items = []
            else:
                # Create a new Sales Invoice
                sales_invoice = frappe.new_doc("Sales Invoice")
                sales_invoice.customer = patient_doc.customer
                sales_invoice.patient = doc.patient
                sales_invoice.set_posting_time = 1
                sales_invoice.posting_date = doc.encounter_date
                
                # Handle None values for due_date
                encounter_date = doc.encounter_date or frappe.utils.nowdate()
                sales_invoice.due_date = encounter_date
                
                sales_invoice.cost_center = doc.medical_department
                sales_invoice.custom_pharmacy_id = doc.name
                sales_invoice.debit_to = receivable_account
                sales_invoice.items = []

            for item in doc.drug_prescription:
                # Append item to the Sales Invoice
                sales_invoice.append("items", {
                        "item_code": item.drug_code,
                        "qty": item.qty,
                        "rate": item.rate,
                        "cost_center": doc.medical_department,
                })
            
            # Save or update the Sales Invoice as a draft
            sales_invoice.save(ignore_permissions=True)
            sales_invoice.submit()
            
            # Update the following fields before committing to the database
            doc.sales_invoice_id = sales_invoice.name
            doc.payment_status = "Payment Pending"
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            frappe.msgprint(_("Sales Invoice {0} created/updated successfully.").format(sales_invoice.name))
             
        except frappe.ValidationError as e:
            frappe.db.rollback()
            frappe.throw(_("There was an error creating the Sales Invoice: {0}").format(str(e)))

        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(message=str(e), title="Sales Invoice Creation Error")
            frappe.throw(_("An unexpected error occurred while creating the Sales Invoice. Please try again or contact support. Error details: {0}").format(str(e)))

@frappe.whitelist()
def pharmacy_status(custom_payment_id):
    # Get all Sales Invoices where custom_payment_id matches and exclude cancelled and drafts
    invoices = frappe.get_all(
        'Sales Invoice',
        filters={
            'patient': custom_payment_id,
            'docstatus': 1  # Only includes submitted documents
        },
        fields=['name', 'outstanding_amount', 'custom_pharmacy_id']
    )
    
    # Extract custom_pharmacy_id from invoices
    pharmacy_ids = [invoice.custom_pharmacy_id for invoice in invoices if invoice.custom_pharmacy_id]
    
    if not pharmacy_ids:
        return "No Pharmacy doc found."

    # Find the corresponding Pharmacy documents
    pharmacies = frappe.get_all(
        'Pharmacy',
        filters={'name': ['in', pharmacy_ids]},
        fields=['name', 'payment_status']
    )

    investigations = []
    
    for pharmacy in pharmacies:
        # Fetch the Pharmacy document
        patient_pharmacy = frappe.get_doc('Pharmacy', pharmacy.name)
        updated = False
        
        # Filter invoices matching the current pharmacy
        matching_invoices = [invoice for invoice in invoices if invoice.custom_pharmacy_id == pharmacy.name]
        
        # Check the outstanding amounts
        if all(invoice.outstanding_amount <= 0 for invoice in matching_invoices):
            patient_pharmacy.payment_status = "Fully Paid"
            updated = True
        elif any(invoice.outstanding_amount > 0 for invoice in matching_invoices):
            patient_pharmacy.payment_status = "Partially Paid"
            updated = True
        
        if updated:
            patient_pharmacy.save(ignore_permissions=True)
            investigations.append({
                'pharmacy': patient_pharmacy.name,
                'status': patient_pharmacy.payment_status
            })

    if investigations:
        frappe.db.commit()  # Commit changes to the database

    return investigations or "No updates were made to Pharmacy documents."
