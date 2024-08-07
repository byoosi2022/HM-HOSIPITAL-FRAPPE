import frappe
from frappe import _

@frappe.whitelist()
def create_patient_encounter(patient, encounter_date, vital_signs, practitioner):
    try:
        # Retrieve the Patient document
        patient_doc = frappe.get_doc('Patient', patient)
        
        # Check if a Vital Signs document already exists for this patient
        existing_encounters = frappe.get_all("Patient Encounter", filters={
            "custom_vitals_id": vital_signs,
        })
        
        if existing_encounters:
            return {
                "message": _(f"A Patient Encounter with Vital Signs {vital_signs} already exists.")
            }
        
        # Create a new Patient Encounter document
        patient_encounter = frappe.get_doc({
            "doctype": "Patient Encounter",
            "patient": patient,
            "encounter_date": encounter_date,
            "custom_cost_center":patient_doc.custom_consulting_doctor,
            "status": "Open",
            "consultation_charge": patient_doc.custom_invoice_no,  # Ensure this field exists in Patient doctype
            "practitioner": practitioner,
            "custom_vitals_id": vital_signs  # Ensure this field exists in Patient Encounter doctype
        })
        patient_encounter.insert(ignore_permissions=True)
        return {"message": _("Direct the Patient to go and See the Doctor. Patient Encounter created successfully.")}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Patient Encounter Creation Error')
        return {"error": str(e)}
