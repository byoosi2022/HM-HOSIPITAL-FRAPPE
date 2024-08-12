import frappe
from frappe import _

@frappe.whitelist()
def update_drugs_payment_status(custom_payment_id):
    # Get all Sales Invoices where custom_payment_id matches and exclude cancelled and drafts
    invoices = frappe.get_all(
        'Sales Invoice',
        filters={
            'patient': custom_payment_id,
            'docstatus': 1  # Only includes submitted documents
        },
        fields=['name', 'outstanding_amount', 'custom_patient_ecounter_id']
    )
    
    # Extract custom_patient_ecounter_id from invoices
    encounter_ids = [invoice.custom_patient_ecounter_id for invoice in invoices if invoice.custom_patient_ecounter_id]
    
    if not encounter_ids:
        return "No encounters found."

    # Find the corresponding Patient Encounter documents
    encounters = frappe.get_all(
        'Patient Encounter',
        filters={'name': ['in', encounter_ids]},
        fields=['name']
    )

    investigations = []
    
    for encounter in encounters:
        patient_encounter = frappe.get_doc('Patient Encounter', encounter.name)
        updated = False

        # Access the child table 'drug Prescription'
        for drugs in patient_encounter.drug_prescription:
            # Check if the drug is already Fully Paid
            if drugs.custom_drug_status != "Fully Paid":
                # Check if any invoice related to this encounter has no outstanding amount
                matching_invoices = [invoice for invoice in invoices if invoice.custom_patient_ecounter_id == encounter.name]
                if all(invoice.outstanding_amount <= 0 for invoice in matching_invoices):
                    drugs.custom_lab_status = "Fully Paid"
                    updated = True
                    investigations.append(drugs)
                    
          
        if updated:
            patient_encounter.save()
            frappe.db.commit()  # Commit changes to the database

    return investigations

