// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt
frappe.ui.form.on('Patient Payment Management', {
    patient: function(frm) {
        populateInvoiceTable(frm);
    },
    on_submit: async function(frm) {
        const success = await submitPayments(frm);
        if (!success) {
            frappe.validated = false; // Prevent the form from saving
        }
    }
});

function populateInvoiceTable(frm) {
    // Clear the existing rows in the child table first
    frm.clear_table('invoice_details');
    frm.refresh_field('invoice_details');

    // Get the filters
    const cost_center = frm.doc.cost_center;
    const posting_date = frm.doc.posting_date;
    const patient = frm.doc.patient;

    if (patient) {
        // Call the server-side method
        frappe.call({
            method: 'hmh_custom_app.custom_api.sales_invoice.get_sales_invoices_with_totals',
            args: {
                cost_center: cost_center,
                posting_date: posting_date,
                patient: patient
            },
            callback: function(response) {
                const invoices = response.message.Invoices;
                if (invoices && invoices.length > 0) {
                    // Add rows to the child table
                    invoices.forEach(invoice => {
                        let child = frm.add_child('invoice_details');
                        frappe.model.set_value(child.doctype, child.name, 'invoice', invoice.name);
                        frappe.model.set_value(child.doctype, child.name, 'outstanding_amount', invoice.outstanding_amount);
                        frappe.model.set_value(child.doctype, child.name, 'posting_date', invoice.posting_date);
                    });

                    // Refresh the child table
                    frm.refresh_field('invoice_details');
                } else {
                    frappe.msgprint(__('No invoices found with the given filters.'));
                }
            },
            error: function(error) {
                frappe.msgprint(__('An error occurred while fetching sales invoices.'));
                console.error(error);
            }
        });
    }
}

async function submitPayments(frm) {
    try {
        const response = await frappe.call({
            method: 'hmh_custom_app.custom_api.patient_payment.create_payments',
            args: {
                patient_payment: frm.doc.name
            },
            freeze: true,
            freeze_message: __('Creating Payment Entries...')
        });

        if (response.message.error) {
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: response.message.error
            });
            return false;
        } else {
            frappe.msgprint({
                title: __('Success'),
                indicator: 'green',
                message: __('Payment Entries created successfully: {0}', [response.message.payment_entries.join(', ')])
            });
            return true;
        }
    } catch (error) {
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('An error occurred while creating payment entries.')
        });
        console.error(error);
        return false;
    }
}





