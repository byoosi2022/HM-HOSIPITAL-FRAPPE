import frappe
from frappe import _

@frappe.whitelist()
def update_drug_payment_status(doc, method):
    # Get all Sales Invoices related to the patient and exclude cancelled and drafts
    invoices = frappe.get_all(
        'Sales Invoice',
        filters={
            'patient': doc.patient,
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
        fields=['name', 'patient']
    )

    investigations = []
    
    for encounter in encounters:
        patient_encounter = frappe.get_doc('Patient Encounter', encounter.name)
        patient_doc = frappe.get_doc('Patient', patient_encounter.patient)
        updated = False

        # Access the child table 'drug Prescription'
        for drugs in patient_encounter.drug_prescription:
            # Check if the drug is already Fully Paid
            if drugs.custom_drug_status != "Fully Paid" and patient_doc.customer_group == "Insurance":
                # Check if any invoice related to this encounter has no outstanding amount
                matching_invoices = [invoice for invoice in invoices if invoice.custom_patient_ecounter_id == encounter.name]
                if all(invoice.outstanding_amount <= 0 for invoice in matching_invoices):
                    drugs.custom_drug_status = "Fully Paid"
                    updated = True
                    investigations.append(drugs)
              

        if updated:
            patient_encounter.save()
            frappe.db.commit()  # Commit changes to the database
            frappe.msgprint(_("Patient Encount{0} Recieved successfully.").format(patient_encounter.name))

    return investigations

   
