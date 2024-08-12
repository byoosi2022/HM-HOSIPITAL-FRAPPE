import frappe
from frappe import _

def on_submit(doc, method):
    if doc.drug_prescription:
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
                                                  "custom_patient_ecounter_id": doc.name,
                                                  "docstatus": 0  # Draft status
                                              }, 
                                              limit=1)
            
            if existing_invoice:
                # Update the existing draft Sales Invoice
                sales_invoice = frappe.get_doc("Sales Invoice", existing_invoice[0].name)
                sales_invoice.set_posting_time = 1
                sales_invoice.cost_center = doc.custom_cost_center
                sales_invoice.posting_date = doc.encounter_date
                
                # Handle None values for due_date
                encounter_date = doc.encounter_date or frappe.utils.nowdate()
                custom_due_date = doc.custom_due_date or encounter_date
                sales_invoice.due_date = max(custom_due_date, encounter_date)
                
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
                custom_due_date = doc.custom_due_date or encounter_date
                sales_invoice.due_date = max(custom_due_date, encounter_date)
                
                sales_invoice.cost_center = doc.custom_cost_center
                sales_invoice.custom_patient_ecounter_id = doc.name
                sales_invoice.debit_to = receivable_account
                sales_invoice.items = []

            # Flag to check if any item should be added
            has_items_to_add = False

            for item in doc.drug_prescription:
                if item.custom_drug_status == "Fully Paid":
                    # Skip items that are already paid
                    continue
                
                if not item.drug_code or not item.custom_amount:
                    frappe.log_error(f"Missing data in custom_items: {item.as_dict()}", "Sales Invoice Creation Error")
                    frappe.throw(_("Missing data for item {0}. Ensure that item code and amount are provided.").format(item.item))
                
                # Append item to the Sales Invoice
                sales_invoice.append("items", {
                        "item_code": item.drug_code,
                        "qty": item.custom_qty,
                        "rate": item.custom_rate,
                        "cost_center": doc.custom_cost_center,
                })
                
                # Set flag to true if at least one item is added
                has_items_to_add = True

            if not has_items_to_add:
                # If no items are added, show message and proceed
                frappe.msgprint(_("No valid Prescripions found"), raise_exception=False)
            else:
                # Save or update the Sales Invoice as a draft
                sales_invoice.save(ignore_permissions=True)
                # sales_invoice.submit()
                frappe.msgprint(_("Sales Invoice {0} created/updated successfully.").format(sales_invoice.name))
                
                investigations = []
                # Check if the customer group is 'Insurance' and create a Pharmacy Doc
                
                if customer.customer_group == "Insurance" or customer.custom_bill_status == "Bill Later":
                    for drug in doc.drug_prescription:
                        if drug.custom_drug_status != "Fully Paid":
                            drug.custom_drug_status = "Fully Paid"
                            investigations.append(drug)
                            doc.save()
                            frappe.db.commit()  # Commit changes to the database
                            # Fetch the Patient document to get gender 
                            patient_reg = frappe.get_doc('Patient Registration Identification', patient_doc.custom_patient_mrno)
                            # Create a new Pharmacy document 
                            pharmacy_doc = frappe.new_doc('Pharmacy')
                            pharmacy_doc.patient = doc.patient
                            pharmacy_doc.patient_sex = patient_doc.sex
                            pharmacy_doc.patient_age = patient_reg.full_age
                            pharmacy_doc.encounter_date = doc.encounter_date
                            pharmacy_doc.practitioner = doc.practitioner
                            pharmacy_doc.patient_encounter_id = doc.name  
                            pharmacy_doc.medical_department = patient_doc.custom_consulting_department  
                            # Append item to the Sales Invoice 
                            pharmacy_doc.append("drug_prescription", {
                                "drug_code": drug.drug_code,
                                "dosage": drug.dosage,
                                "period": drug.period,
                                "qty": drug.custom_rate,
                                "dosage_form": drug.dosage_form,
                                "strength": drug.strength,
                                "strength_uom": drug.strength_uom,
                            })
                            frappe.log_error(f"Pharmacy doc created for drug {drug.drug_code}", "Pharmacy Creation")
                            pharmacy_doc.save(ignore_permissions=True)
                            frappe.db.commit()  # Commit changes to the database

        except frappe.ValidationError as e:
            frappe.db.rollback()
            frappe.throw(_("There was an error creating the Sales Invoice: {0}").format(str(e)))

        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(message=str(e), title="Sales Invoice Creation Error")
            frappe.throw(_("An unexpected error occurred while creating the Sales Invoice. Please try again or contact support. Error details: {0}").format(str(e)))
