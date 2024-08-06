import frappe
from frappe import _

@frappe.whitelist()
def create_patient_encounter(patient, encounter_date, vital_signs, consultation_charge, practitioner):
    try:
        # Create a new Patient Encounter document
        patient_encounter = frappe.get_doc({
            "doctype": "Patient Encounter",
            "patient": patient,
            "encounter_date": encounter_date,
            "vital_signs": vital_signs,
            "status": "Open",
            "consultation_charge": consultation_charge,
            "practitioner": practitioner
        })
        patient_encounter.insert(ignore_permissions=True)
        return {"message": _("Draft Patient Encounter created successfully.")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Patient Encounter Creation Error')
        return {"error": str(e)}
