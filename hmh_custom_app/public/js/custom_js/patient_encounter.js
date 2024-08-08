frappe.ui.form.on('Patient Encounter', {
    custom_get_patients_bill: function(frm) {
        update_custom_items_table(frm);
    },
    custom_get_bills: function(frm) {
        update_items_table(frm);
    },
    custom_view_traige: function(frm) {
        viewTriage(frm);
    },
});


frappe.ui.form.on('Expense Claim Items', {
    amount: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    }
});
frappe.ui.form.on('drug_prescription', {
    item_code: function(frm, cdt, cdn) {
        var item = frappe.get_doc(cdt, cdn);
        if (frm.doc.price_list) {
            frappe.model.set_value(cdt, cdn, 'price_list', frm.doc.price_list);
        }
    }
});

function update_custom_items_table(frm) {
    frappe.call({
        method: 'hmh_custom_app.custom_api.patient_encounter.on_submit',
        args: {
            patient_encounter: frm.doc.name
        },
        callback: function(r) {
            if (r.message.status === 'success') {
                frappe.msgprint(r.message.message);
                // Refresh the custom_items table to reflect the changes
                frm.refresh_field('custom_items');
                // Reload the page
                location.reload();
            } else {
                frappe.msgprint(__('Error: ') + r.message.message);
            }
        },
        error: function(r) {
            frappe.msgprint(__('Server call failed.'));
        }
    });
}

function update_items_table(frm) {
    frappe.call({
        method: 'hmh_custom_app.custom_api.encounter.on_submit',
        args: {
            patient_encounter: frm.doc.name
        },
        callback: function(r) {
            if (r.message.status === 'success') {
                frm.set_value('custom_total_amount', r.message.sums.drug_sum);
                frm.set_value('custom_total_investigations', r.message.sums.lab_test_sum);
                frm.set_value('custom_total_clinical_procedures', r.message.sums.procedure_sum);
                frm.set_value('custom_total_therapies', r.message.sums.therapy_sum);
                frm.set_value('custom_total_service_request', r.message.sums.service_sum);
                 frm.save();
                 
            } else {
                frappe.msgprint(__('Error: ') + r.message.message);
            }
        },
        error: function(r) {
            frappe.msgprint(__('Server call failed.'));
        }
    });
}

