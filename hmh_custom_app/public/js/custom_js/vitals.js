frappe.ui.form.on('Vital Signs', {
    before_save: function (frm) {
        frappe.call({
            method: 'hmh_custom_app.custom_api.vitals.create_patient_encounter',
            args: {
                patient: frm.doc.patient,
                encounter_date: frm.doc.signs_date,
                vital_signs: frm.doc.name,
                consultation_charge: frm.doc.custom_invoice_no,
                practitioner: frm.doc.custom_practionaer // Ensure the field name is correct
            },
            callback: function (response) {
                if (!response.exc) {
                    frappe.msgprint(__('Draft Patient Encounter created successfully.'));
                } else {
                    frappe.msgprint(__('Error creating Patient Encounter: ' + response.exc));
                }
            },
            error: function (error) {
                frappe.msgprint(__('An error occurred: ' + error.message));
            }
        });
    }
});
