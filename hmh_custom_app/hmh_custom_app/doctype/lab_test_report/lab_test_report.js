// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Lab Test Report", {
// 	refresh(frm) {

// 	},
// });

// frappe.ui.form.on('Lab Test Report', {
//     refresh: function(frm) {
//         // Add a button to fetch lab tests
//         frm.add_custom_button('Fetch Lab Tests', function() {
//             const patient = frm.doc.patient; // Assuming you have a patient field in your form
            
//             if (!patient) {
//                 frappe.msgprint(__('Please select a patient first.'));
//                 return;
//             }

//             // Call the backend function
//             frappe.call({
//                 method: 'hmh_custom_app.custom_api.reports.latest_test.fetch_patient_labtest',
//                 args: {
//                     patient: patient
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         // Handle the response here
//                         const result = response.message;
//                         console.log(result)
                   
//                     }
//                 },
//                 error: function(err) {
//                     frappe.msgprint(__('Error fetching lab tests.'));
//                 }
//             });
//         });
//     }
// });


frappe.ui.form.on('Lab Test Report', {
    patient: function(frm) {
        if (frm.doc.patient) {
            // Fetch patient lab test details from the backend
            frappe.call({
                method: "hmh_custom_app.custom_api.reports.latest_test.fetch_patient_labtest",  // Your backend method to fetch lab tests
                args: {
                    patient: frm.doc.patient  // Assuming the 'patient' field is present in the form
                },
                callback: function(response) {
                    if (response.message) {
                        let data = response.message;

                        // Populate patient details in the form
                        frm.set_value('patient_name', data.patient_details.name);
                        frm.set_value('age', data.patient_details.age);
                        frm.set_value('sex', data.patient_details.sex);

                        // Clear existing child table (report_details)
                        frm.clear_table('report_details');

                        // Loop through the grouped lab test results by date
                        for (let date in data.lab_tests_grouped) {
                            let date_group = data.lab_tests_grouped[date];

                            // Loop through each test within that date
                            for (let test_key in date_group) {
                                let test_data = date_group[test_key];

                                // Process descriptive tests
                                test_data.descriptive_tests.forEach(function(test) {
                                    let child_row = frm.add_child('report_details');

                                    // Set values in the child table
                                    child_row.test_name = test.lab_test_particulars;       // Test name (WBC, RBC, etc.)
                                    child_row.result_value = test.result_value;            // Result value (e.g., "wee")
                                    child_row.lab_technician_name = test.employee;         // Lab technician (if available)
                                    child_row.doctor_name = test.practitioner_name;        // Doctor name
                                    child_row.date = date;                                // Test date
                                    child_row.time = frappe.datetime.now_time();           // Current time

                                    // Refresh the child table to show added row
                                    frm.refresh_field('report_details');
                                });
                            }
                        }
                    }
                }
            });
        }
    }
});


