frappe.ui.form.on('Vital Signs', {
    on_submit: function (frm) {
        frappe.call({
            method: 'hmh_custom_app.custom_api.vitals.create_patient_encounter',
            args: {
                patient: frm.doc.patient,
                encounter_date: frm.doc.signs_date,
                vital_signs: frm.doc.name,
                practitioner: frm.doc.custom_practionaer // Ensure the field name is correct
            },
            callback: function (response) {
                if (!response.exc) {
                    frappe.msgprint(__('Direct the Patient to go and See the Doctor. Patient Encounter created successfully.'));
                } else {
                    frappe.msgprint(__('Error creating Patient Encounter: ' + response.message));
                }
            },
            error: function (error) {
                frappe.msgprint(__('An error occurred: ' + error.message));
            }
        });
    }
});
