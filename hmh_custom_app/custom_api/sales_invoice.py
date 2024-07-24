import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def create_sales_invoice(patient_payment):
    try:
        # Get the patient payment document
        patie_payment_doc = frappe.get_doc("Collect Patient Payment", patient_payment)
        patient = patie_payment_doc.patient
        
        # Fetch the patient document linked in the patient payment
        patient_doc = frappe.get_doc("Patient", patient)

        # Check if a Sales Invoice already exists for the patient
        existing_invoice = frappe.db.exists("Sales Invoice", {"patient": patient, "docstatus": 0})
        if existing_invoice:
            return {
                "message": _("A sales invoice already exists for this patient.")
            }

        # Create a Sales Invoice
        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.patient = patient
        sales_invoice.company = frappe.defaults.get_global_default("company")
        sales_invoice.customer = patient_doc.customer
        sales_invoice.due_date = frappe.utils.add_days(frappe.utils.nowdate(), 30)
        sales_invoice.set_posting_time = 1
        sales_invoice.posting_date = patie_payment_doc.posting_date
        sales_invoice.posting_time = patie_payment_doc.posting_time

        # Add items from patie_payment_doc.items to sales_invoice.items
        for item in patie_payment_doc.items:
            sales_invoice.append("items", {
                "item_code": item.item_code,
                "rate": item.rate,
                "qty": item.qty
            })

        # Save the Sales Invoice
        sales_invoice.insert()

        # Optionally, submit the Sales Invoice
        # sales_invoice.submit()

        return {
            "sales_invoice_name": sales_invoice.name,
            "message": _("Sales Invoice {0} created successfully.").format(sales_invoice.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Sales Invoice Creation Error')
        return {
            "error": str(e)
        }
