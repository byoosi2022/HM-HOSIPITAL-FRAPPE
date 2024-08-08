import frappe

def create_vital_signs_for_patient(doc, method=None):
    # Check if a draft Vital Signs document already exists for this patient
    existing_vital_signs = frappe.get_all("Vital Signs", filters={
        "patient": doc.name,
        "custom_patient_status": "Seen The Receptionist",
        # "docstatus": 0  # Ensure it's in draft state
    })

    if not existing_vital_signs:
        # Create a new Vital Signs document in draft state
        try:
            vital_signs = frappe.get_doc({
                "doctype": "Vital Signs",
                "patient": doc.name,
                "custom_practionaer": doc.custom_consulting_doctor,
                "custom_patient_status": "Seen The Receptionist",
                "custom_customer_type": doc.customer_group,
                "custom_invoice_no": doc.custom_invoice_no,
            })
            vital_signs.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to create Vital Signs for patient {doc.name}: {str(e)}", "Vital Signs Creation Error")

