import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist()
def create_sales_invoice(patient_form):
    try:
        # Get the patient information from the Patient form
        patient_doc = frappe.get_doc("Patient", patient_form)
        # patient = patient_doc.name

        # Check if a Sales Invoice already exists for the patient
        existing_payment = frappe.db.exists({
            'doctype': 'Collect Patient Payment',
            'patient_id': patient_form,
            'docstatus': ['!=', 2]  # Exclude canceled documents
        })
        if existing_payment:
            return {
                "message": _("Consultation Fees already exist for this patient.")
            }

        # Create a new Collect Patient Payment document
        patient_payment = frappe.new_doc("Collect Patient Payment")
        patient_payment.patient = patient_form
        patient_payment.patient_name = patient_doc.patient_name
        patient_payment.patient_id = patient_form
        patient_payment.doctor = patient_doc.custom_consulting_doctor
        patient_payment.posting_date = patient_doc.custom_date
        patient_payment.posting_time = patient_doc.custom_time
        patient_payment.patient_mrno = patient_doc.custom_patient_mrno
        patient_payment.cost_center = patient_doc.custom_consulting_department
        patient_payment.customer_group = patient_doc.customer_group
        patient_payment.price_list = patient_doc.default_price_list
        patient_payment.custom_customer = patient_doc.customer
        patient_payment.company = frappe.defaults.get_global_default("company")
        patient_payment.grand_totals = patient_doc.custom_fee
        patient_payment.total_paid_amount = patient_doc.custom_fee
        patient_payment.total_qty = 1

        # Verify that custom_fee and custom_consultation fields exist 
        if not patient_doc.custom_consultation or not patient_doc.custom_fee:
            return {
                "message": _("Consultation item or fee is missing in the patient record.")
            }
        
        
        patient_payment.append("cash_items", {
            "mode_of_payment": patient_doc.custom_mode_of_payment,
            "transaction_id": patient_doc.transaction_id,
            "paid_amount": patient_doc.custom_fee
            
        })

        patient_payment.append("items", {
            "item_code": patient_doc.custom_consultation,
            "rate": patient_doc.custom_fee,
            "amount": patient_doc.custom_fee,
            "qty": 1
        })

        # Save and submit the Collect Patient Payment document
        patient_payment.insert()
        patient_payment.submit()

        return {
            "sales_invoice_name": patient_payment.name,
            "message": _("Patient Consultation Payment {0} created successfully.").format(patient_payment.name)
        }
    except frappe.DoesNotExistError:
        return {
            "message": _("The specified patient does not exist.")
        }
    except Exception as e:
        return {
            "message": _("An error occurred while creating the payment: {0}").format(str(e))
        }



# In your custom Python module (e.g., hmh_custom_app/custom_api/Patient.py)


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
                "custom_patient_status": "Seen The Receptionist"
            })
            vital_signs.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to create Vital Signs for patient {doc.name}: {str(e)}", "Vital Signs Creation Error")


