// frappe.ui.form.on('Patient', {
//     before_save: function (frm) {
//         if (!frm.doc.phone && frm.doc.contact && frm.doc.contact.match && frm.doc.contact.match(/^\d{9,12}$/)) {
//             frm.doc.phone = frm.doc.contact;
//         }

//         // if (frm.doc.custom_bill_status != "Bill Sent") {
//         //     frappe.msgprint(__('You have.'));

//         // } 
//     },

//     customer_group: function (frm) {
//         checkUserRoleAndAddButtons(frm);

//     },      
    
//     refresh: function (frm) {

//         // Add event listener for custom_patient_mrno selection
//         frm.fields_dict['custom_patient_mrno'].df.onchange = function () {
//             // Clear age, month, and day fields
//             document.querySelector('#dob-day').value = '';
//             document.querySelector('#dob-mon').value = '';
//             document.querySelector('#dob-age').value = '';
//             document.querySelector('#dob-year').value = '';

//             // Set the DOB value to null to trigger a reset
//             frm.set_value('dob', '');

//             if (frm.doc.custom_patient_mrno) {
//                 // Fetch data from Patient Registration Identification
//                 frappe.db.get_value('Patient Registration Identification', frm.doc.custom_patient_mrno, ['full_age', 'day', 'month', 'patient_name'])
//                     .then(r => {
//                         if (r.message) {
//                             console.log(r.message);
//                             if (r.message.full_age || r.message.month || r.message.day) {
//                                 setAgeValues(r.message.full_age, r.message.month, r.message.day);
//                             }
//                         }
//                     });

//                 frappe.db.get_value('Patient Registration Identification', frm.doc.custom_patient_mrno, 'patient_name')
//                     .then(r => {
//                         if (r.message && r.message.patient_name) {
//                             let patient_name = r.message.patient_name;
//                             let name_parts = patient_name.split(' ');

//                             if (name_parts.length === 2) {
//                                 frm.set_value('first_name', name_parts[0]);
//                                 frm.set_value('last_name', name_parts[1]);
//                                 frm.set_value('middle_name', '');
//                             } else if (name_parts.length === 3) {
//                                 frm.set_value('first_name', name_parts[0]);
//                                 frm.set_value('middle_name', name_parts[1]);
//                                 frm.set_value('last_name', name_parts[2]);
//                             } else if (name_parts.length > 3) {
//                                 frm.set_value('first_name', name_parts[0]);
//                                 frm.set_value('last_name', name_parts[name_parts.length - 1]);
//                                 frm.set_value('middle_name', name_parts.slice(1, -1).join(' '));
//                             } else {
//                                 frm.set_value('first_name', patient_name);
//                                 frm.set_value('middle_name', '');
//                                 frm.set_value('last_name', '');
//                             }
//                         }
//                     });
//             }
//         };

//         // Rest of the code
//         const dob = document.querySelector("input[data-fieldname='dob']");
//         const referenceNode = dob;
//         if (!document.querySelector('#ageInputControl')) {
//             const newNode = document.createElement('div');
//             newNode.setAttribute('id', 'ageInputControl');
//             newNode.style = 'display:flex;flex-flow:row wrap;justify-content: space-around';
//             newNode.innerHTML = `
//         <label style='width:25%;' class='control-label'>Day</label>
//         <label style='width:25%;' class='control-label'>Month</label>
//         <label style='width:25%;' class='control-label'>Age</label>
//         <label style='width:25%;' class='control-label'>Year</label>
//         <br>
//         <input style='width:25%;' id='dob-day' type='number' placeholder='1' min='1' max='31' class='input-with-feedback form-control bold'></input>
//         <input style='width:25%;' id='dob-mon' type='number' placeholder='1' min='1' max='12' class='input-with-feedback form-control bold'></input>
//         <input style='width:25%;' id='dob-age' type='number' placeholder='0' class='input-with-feedback form-control bold'></input>
//         <input style='width:25%;' id='dob-year' type='number' placeholder='0' class='input-with-feedback form-control bold'></input>
//         <br><br>`;
//             referenceNode.parentNode.insertBefore(newNode, referenceNode);

//             let dv = 1, mv = 1, av = 0, yv = new Date().getFullYear();

//             let setdob = (useY) => {
//                 dv = dv.toString().length == 1 ? '0' + dv : dv;
//                 mv = mv.toString().length == 1 ? '0' + mv : mv;
//                 let dobv = `${useY ? yv : new Date().getFullYear() - av}-${mv}-${dv}`;
//                 frm.set_value('dob', dobv);
//                 tooltip();
//             };

//             function tooltip() { }

//             let iday = document.querySelector('#dob-day');
//             iday.onchange = dayChange;
//             iday.onfocuschange = dayChange;

//             function dayChange() {
//                 dv = Math.abs(this.value || 1);
//                 dv = dv > 31 ? 31 : dv < 1 ? 1 : parseInt(dv);
//                 this.value = dv;
//                 setdob();
//             }

//             let imonth = document.querySelector('#dob-mon');
//             imonth.onchange = monthChange;
//             imonth.onfocuschange = monthChange;

//             function monthChange() {
//                 mv = Math.abs(this.value || 1);
//                 mv = mv > 12 ? 12 : mv < 1 ? 1 : parseInt(mv);
//                 this.value = mv;
//                 setdob();
//             }

//             let iyear = document.querySelector('#dob-year');
//             let iage = document.querySelector('#dob-age');
//             iage.onchange = ageChange;
//             iage.onfocuschange = ageChange;

//             function ageChange() {
//                 av = Math.abs(parseInt(this.value || 0));
//                 av = av < 0 ? 0 : av > 200 ? 200 : av;
//                 this.value = av;
//                 iyear.value = new Date().getFullYear() - av;
//                 setdob();
//             }

//             iyear.onchange = yChange;
//             iyear.onfocuschange = yChange;

//             function yChange() {
//                 yv = Math.abs(this.value || 1900);
//                 yv = yv > new Date().getFullYear() ? new Date().getFullYear() : yv < 1900 ? 1900 : parseInt(yv);
//                 this.value = yv;
//                 iage.value = new Date().getFullYear() - yv;
//                 setdob(true);
//             }

//             function setAgeValues(full_age, month, day) {
//                 av = full_age || 0;
//                 mv = month || 1;
//                 dv = day || 1;
//                 yv = new Date().getFullYear() - av;
//                 document.querySelector('#dob-year').value = yv;
//                 document.querySelector('#dob-age').value = av;
//                 document.querySelector('#dob-mon').value = mv;
//                 document.querySelector('#dob-day').value = dv;
//                 setdob(true);
//             }

//             function age_html() {
//                 let cal = document.querySelector(`[data-fieldname='age_html']`);
//                 let diff = frappe.datetime.get_diff(frappe.datetime.get_today(), `${new Date().getFullYear() - (iage.value || 0)}-${mv}-${dv}`);
//                 let yrs = 0;
//             }
//         }

//         var consultation_item = "Consultation";

//         frappe.call({
//             method: 'frappe.client.get_list',
//             args: {
//                 doctype: 'Item',
//                 filters: { item_group: consultation_item },
//                 limit: 1
//             },
//             callback: function (response) {
//                 if (response.message && response.message.length > 0) {
//                     frm.set_query('custom_consultation', function () {
//                         return {
//                             filters: { item_group: consultation_item }
//                         };
//                     });
//                 }
//             }
//         });


//         // Ensure this runs after the form is loaded or when appropriate
//         if (!frm.doc.__islocal) {  // Ensure the buttons are not shown on a new document
//             checkUserRoleAndAddButtons(frm);
//         }
  
//     },
//     custom_consultation: function (frm) {
//         if (frm.doc.custom_consultation) {
//             frappe.call({
//                 method: 'frappe.client.get_value',
//                 args: {
//                     doctype: 'Item Price',
//                     filters: {
//                         item_code: frm.doc.custom_consultation,
//                         price_list: frm.doc.default_price_list,
//                         selling: 1
//                     },
//                     fieldname: 'price_list_rate'
//                 },
//                 callback: function (response) {
//                     if (response.message) {
//                         frm.set_value('custom_fee', response.message.price_list_rate);
//                     }
//                 }
//             });
//         }
//     },
//     custom_patient_mrno: function (frm) {
//         if (frm.doc.custom_patient_mrno) {
//             // Fetch the Patient Registration Identification linked by custom_patient_mrno
//             frappe.call({
//                 method: 'frappe.client.get_list',
//                 args: {
//                     doctype: 'Patient Registration Identification',
//                     filters: { 'name': frm.doc.custom_patient_mrno },
//                     fields: ['name', 'customer', 'visit']
//                 },
//                 callback: function (response) {
//                     let patient_reg_id = response.message;
//                     if (patient_reg_id && patient_reg_id.length > 0) {
//                         let patient_reg_doc_name = patient_reg_id[0].name;
//                         // Fetch the Patient Registration Identification document
//                         frappe.call({
//                             method: 'frappe.client.get',
//                             args: {
//                                 doctype: 'Patient Registration Identification',
//                                 name: patient_reg_doc_name
//                             },
//                             callback: function (response) {
//                                 let patient_reg_doc = response.message;
//                                 if (patient_reg_doc) {
//                                     if (!patient_reg_doc.customer) {
//                                         // Update the customer field in Patient Registration Identification visit 
//                                         patient_reg_doc.customer = frm.doc.customer;
//                                         patient_reg_doc.date_of_birth = frm.doc.dob
//                                         patient_reg_doc.visit = "First Time Visit";
//                                         frappe.call({
//                                             method: 'frappe.client.save',
//                                             args: {
//                                                 doc: patient_reg_doc
//                                             },
//                                             callback: function (response) {
//                                                 console.log('Patient Registration Identification updated successfully');
//                                             }
//                                         });
//                                     }

//                                     if (patient_reg_doc.customer && patient_reg_doc.visit) {
//                                         // Set the custom patient field in the Patient doctype
//                                         frm.set_value('re_attendance', 'Existing Customer');
//                                         frm.set_value('custom_attendance', 'Re-Attendance');
//                                         frm.set_value('customer', patient_reg_doc.customer);
//                                     }
//                                 }
//                             }
//                         });
//                     }
//                 }
//             });
//         }
//     }
// });



// function handlePayment(frm, payment_type) {
//     let method = payment_type === 'pay_later'
//         ? 'hmh_custom_app.custom_api.sales_invoice.collect_invoices'
//         : 'hmh_custom_app.custom_api.sales_invoice.collect_invoices';

//     frappe.call({
//         method: method,
//         args: {
//             patient: frm.doc.name
//         },
//         callback: function (r) {
//             if (r.message) {
//                 if (r.message.error) {
//                     frappe.msgprint({
//                         title: __('Error'),
//                         indicator: 'red',
//                         message: r.message.error
//                     });
//                 } else {
//                     frappe.msgprint({
//                         title: __('Success'),
//                         indicator: 'green',
//                         message: r.message.message
//                     });
//                 }
//             } else {
//                 frappe.msgprint({
//                     title: __('Information'),
//                     indicator: 'orange',
//                     message: __('No response message received.')
//                 });
//             }
//         },
//         error: function (err) {
//             frappe.msgprint({
//                 title: __('Error'),
//                 indicator: 'red',
//                 message: __('An error occurred: ' + err.message)
//             });
//         }
//     });
// }

// function checkUserRoleAndAddButtons(frm) {
//     // Check if the customer group on the patient is "Insurance"
//     if (frm.doc.customer_group === "Insurance") {
//         // Hide "Pay Now" and "Pay Later" buttons
//         frm.remove_custom_button(__('Pay Now'));
//         frm.remove_custom_button(__('Pay Later'));

//         // Show "Create Bill" button
//         frm.add_custom_button(__('Create Bill'), function () {
//             createBill(frm);
//         });
//     } else {
//         // If the customer group is not "Insurance", proceed with existing role-based button logic
//         frappe.call({
//             method: 'hmh_custom_app.custom_api.get_role.get_user_roles',
//             args: {},
//             callback: function (r) {
//                 if (r.message) {
//                     // Add "Pay Now" button for all users
//                     frm.add_custom_button(__('Pay Now'), function () {
//                         handlePayment(frm, 'pay_now');
//                     });

//                     if (r.message.roles.includes('Pay Later')) {
//                         // Add "Pay Later" button if the user has the role
//                         frm.add_custom_button(__('Pay Later'), function () {
//                             handlePayment(frm, 'pay_later');
//                         });
//                     }
//                 } else {
//                     frappe.msgprint({
//                         title: __('Information'),
//                         indicator: 'orange',
//                         message: __('No user roles received.')
//                     });
//                 }
//             },
//             error: function (err) {
//                 frappe.msgprint({
//                     title: __('Error'),
//                     indicator: 'red',
//                     message: __('An error occurred while fetching user roles: ' + err.message)
//                 });
//             }
//         });
//     }
// }

// function createBill(frm) {
//     // Define the method to call
//     let method = 'hmh_custom_app.custom_api.sales_invoice.collect_invoices';

//     // Make the server call to collect invoices
//     frappe.call({
//         method: method,
//         args: {
//             patient: frm.doc.name
//         },
//         callback: function (r) {
//             if (r.message) {
//                 if (r.message.error) {
//                     // Display an error message if there is an error
//                     frappe.msgprint({
//                         title: __('Error'),
//                         indicator: 'red',
//                         message: r.message.error
//                     });
//                 } else {
//                     // Display a success message if the operation is successful
//                     frappe.msgprint({
//                         title: __('Success'),
//                         indicator: 'green',
//                         message: r.message.message
//                     });
//                 }
//             } else {
//                 // Handle case where there is no message in the response
//                 frappe.msgprint({
//                     title: __('Information'),
//                     indicator: 'orange',
//                     message: __('No response message received.')
//                 });
//             }
//         },
//         error: function (err) {
//             // Handle any errors that occur during the call
//             frappe.msgprint({
//                 title: __('Error'),
//                 indicator: 'red',
//                 message: __('An error occurred: ' + err.message)
//             });
//         }
//     });
// }

// function update_patient_bill_status(frm) {
//     // Call the server-side method to update patient bill status
//     frappe.call({
//         method: 'hmh_custom_app.custom_api.patient.update_patient_bill_status',
//         args: {
//             'custom_payment_id': frm.doc.name
//         },
//         callback: function(response) {
//             if (response.message) {
//                 frappe.msgprint(response.message);
//             }
//         }
//     });
// }




