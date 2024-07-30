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
        existing_invoice = frappe.db.exists("Sales Invoice", {"custom_collection_payment_id": patie_payment_doc.name})
        if existing_invoice:
            return {
                "message": _(f"A sales invoice already exists for this. {patie_payment_doc.name}.")
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
        sales_invoice.selling_price_list = patie_payment_doc.price_list
        sales_invoice.custom_collection_payment_id = patie_payment_doc.name
        sales_invoice.cost_center = patie_payment_doc.cost_center
        sales_invoice.additional_discount_account = patie_payment_doc.discount_account
        sales_invoice.discount_amount = patie_payment_doc.discount

        # Add items from patie_payment_doc.items to sales_invoice.items
        for item in patie_payment_doc.items:
            sales_invoice.append("items", {
                "item_code": item.item_code,
                "rate": item.rate,
                "qty": item.qty,
                "cost_center": patie_payment_doc.cost_center,
            })

        # Save the Sales Invoice
        sales_invoice.insert()

        # Optionally, submit the Sales Invoice
        sales_invoice.submit()

        # Check Sales Invoice status and outstanding amount
        sales_invoice.reload()
        if sales_invoice.status == "Paid" and sales_invoice.outstanding_amount == 0:
            patie_payment_doc.bill_status = "CLOSED"
        else:
            patie_payment_doc.bill_status = "OPEN"

        # Save the updated patient payment document
        patie_payment_doc.save()

        return {
            "sales_invoice_name": sales_invoice.name,
            "message": _("Sales Invoice {0} created successfully.").format(sales_invoice.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Sales Invoice Creation Error')
        return {
            "error": str(e)
        }

@frappe.whitelist()
def create_sales_invoice_payments(patient_payment):
    try:
        # Get the patient payment document
        patie_payment_doc = frappe.get_doc("Collect Patient Payment", patient_payment)
        patient = patie_payment_doc.patient

        # Fetch the patient document linked in the patient payment
        patient_doc = frappe.get_doc("Patient", patient)

        # Check if a Sales Invoice already exists for the patient
        existing_invoice = frappe.db.exists("Sales Invoice", {"custom_collection_payment_id": patie_payment_doc.name})
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
        sales_invoice.selling_price_list = patie_payment_doc.price_list
        sales_invoice.custom_collection_payment_id = patie_payment_doc.name
        sales_invoice.cost_center = patie_payment_doc.cost_center
        sales_invoice.additional_discount_account = patie_payment_doc.discount_account
        sales_invoice.discount_amount = patie_payment_doc.discount

        # Add items from patie_payment_doc.items to sales_invoice.items
        for item in patie_payment_doc.items:
            sales_invoice.append("items", {
                "item_code": item.item_code,
                "rate": item.rate,
                "cost_center": patie_payment_doc.cost_center,
                "qty": item.qty
            })

        # Save the Sales Invoice
        sales_invoice.insert()

        # Optionally, submit the Sales Invoice
        sales_invoice.submit()

        # Fetch the exchange rate (Assuming that payment currency is same as invoice currency)
        target_exchange_rate = frappe.db.get_value("Currency Exchange", 
                                                   {"from_currency": sales_invoice.currency, 
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
            payment_entry.company = sales_invoice.company
            payment_entry.paid_amount = mode.paid_amount
            payment_entry.received_amount = mode.paid_amount
            payment_entry.reference_no = mode.transaction_id
            payment_entry.custom_colection_payment_id = patie_payment_doc.name
            payment_entry.reference_date = patie_payment_doc.posting_date
            payment_entry.target_exchange_rate = target_exchange_rate
            payment_entry.mode_of_payment = mode.mode_of_payment 
            payment_entry.cost_center = patie_payment_doc.cost_center

            # Set required fields
            payment_entry.paid_to = default_paid_to_account
            payment_entry.paid_to_account_currency = account_currency

            # Link the payment to the Sales Invoice
            payment_entry.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": sales_invoice.name,
                "total_amount": sales_invoice.grand_total,
                "outstanding_amount": sales_invoice.grand_total,
                "allocated_amount": mode.paid_amount
            })

            # Save and submit the Payment Entry
            payment_entry.insert()
            payment_entry.submit()
            payment_entries.append(payment_entry.name)

        # Check Sales Invoice status and outstanding amount
        sales_invoice.reload()
        if sales_invoice.status == "Paid" and sales_invoice.outstanding_amount == 0:
            patie_payment_doc.bill_status = "CLOSED"
        else:
            patie_payment_doc.bill_status = "OPEN"

        # Save the patient payment document with updated bill_status
        patie_payment_doc.save()
  
        return {
            "sales_invoice_name": sales_invoice.name,
            "payment_entry_names": payment_entries,
            "message": _("Sales Invoice {0} and Payment Entries {1} created successfully.").format(sales_invoice.name, ", ".join(payment_entries))
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Sales Invoice and Payment Entry Creation Error')
        return {
            "error": str(e)
        }
