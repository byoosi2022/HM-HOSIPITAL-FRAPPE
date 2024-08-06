 
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def create_payments(patient_payment):
    try:
        # Fetch the patient payment document
        if not frappe.db.exists("Patient Payment Management", patient_payment):
            return {
                "error": _("Patient Payment Management {0} not found").format(patient_payment)
            }
        
        patie_payment_doc = frappe.get_doc("Patient Payment Management", patient_payment)
        patient = patie_payment_doc.patient
        company = patie_payment_doc.company

        # Fetch the patient document linked in the patient payment
        if not frappe.db.exists("Patient", patient):
            return {
                "error": _("Patient {0} not found").format(patient)
            }
        
        patient_doc = frappe.get_doc("Patient", patient)

        # Fetch the exchange rate (Assuming that payment currency is same as invoice currency)
        target_exchange_rate = frappe.db.get_value("Currency Exchange", 
                                                   {"from_currency": patie_payment_doc.currency,
                                                    "to_currency": frappe.defaults.get_global_default("default_currency")},
                                                   "exchange_rate")
        if not target_exchange_rate:
            target_exchange_rate = 1  # Default to 1 if no specific exchange rate is found

        # Create Payment Entries for each mode of payment
        payment_entries = []
        for mode in patie_payment_doc.cash_items:
            # Fetch the default account from the Mode of Payment Account child table
            default_paid_to_account = frappe.db.get_value("Mode of Payment Account", 
                                                          {"parent": mode.mode_of_payment, "company": patie_payment_doc.company}, 
                                                          "default_account")
            if not default_paid_to_account:
                return {
                    "error": _("Default account not found for mode of payment {0} and company {1}").format(mode.mode_of_payment, patie_payment_doc.company)
                }
            
            account_currency = frappe.db.get_value("Account", default_paid_to_account, "account_currency")

            payment_entry = frappe.new_doc("Payment Entry")
            payment_entry.payment_type = "Receive"
            payment_entry.party_type = "Customer"
            payment_entry.party = patient_doc.customer
            payment_entry.posting_date = frappe.utils.nowdate()
            payment_entry.company = company
            payment_entry.paid_amount = mode.paid_amount
            payment_entry.received_amount = mode.paid_amount
            payment_entry.reference_no = mode.transaction_id
            payment_entry.custom_payment_id = patie_payment_doc.name
            payment_entry.reference_date = patie_payment_doc.posting_date
            payment_entry.target_exchange_rate = target_exchange_rate
            payment_entry.mode_of_payment = mode.mode_of_payment 
            payment_entry.cost_center = patie_payment_doc.cost_center

            # Set required fields
            payment_entry.paid_to = default_paid_to_account
            payment_entry.paid_to_account_currency = account_currency

            # Link the payment to the Sales Invoice
            allocated_amount = mode.paid_amount
            for invoice in patie_payment_doc.invoice_details:
                if allocated_amount <= 0:
                    break
                invoice_outstanding = frappe.db.get_value("Sales Invoice", invoice.invoice, "outstanding_amount")
                if invoice_outstanding > 0:
                    allocated = min(invoice_outstanding, allocated_amount)
                    payment_entry.append("references", {
                        "reference_doctype": "Sales Invoice",
                        "reference_name": invoice.invoice,
                        "total_amount": invoice_outstanding,
                        "outstanding_amount": invoice_outstanding,
                        "allocated_amount": allocated
                    })
                    allocated_amount -= allocated

            # Save and submit the Payment Entry
            payment_entry.insert()
            payment_entry.submit()
            payment_entries.append(payment_entry.name)

        return {
            "payment_entries": payment_entries
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Payment Entry Creation Error')
        return {
            "error": str(e)
        }
