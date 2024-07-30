frappe.ui.form.on('Patient', {
    before_save: function(frm) {
        if (!frm.doc.phone && frm.doc.contact && frm.doc.contact.match && frm.doc.contact.match(/^\d{9,12}$/)) {
            frm.doc.phone = frm.doc.contact;
        }
    },
    refresh: function(frm) {
        
        frm.add_custom_button(__('Get Consulation Fees'), function() {
            frappe.call({
                method: "hmh_custom_app.custom_api.patient.create_sales_invoice",
                args: {
                    patient_form: frm.doc.name
                },
                callback: function(response) {
                    console.log(response)
                    if (response.message) {
                        frappe.msgprint(response.message);
                    }
                }
            });
        });
        // Add event listener for custom_patient_mrno selection
        frm.fields_dict['custom_patient_mrno'].df.onchange = function() {
            if (frm.doc.custom_patient_mrno) {
                frappe.db.get_value('Patient Registration Identification', frm.doc.custom_patient_mrno, 'full_age')
                    .then(r => {
                        if (r.message && r.message.full_age) {
                            let full_age = r.message.full_age;
                            document.querySelector('#dob-age').value = full_age;
                            setAgeValues(full_age);
                        }
                    });
                
                frappe.db.get_value('Patient Registration Identification', frm.doc.custom_patient_mrno, 'patient_name')
                    .then(r => {
                        if (r.message && r.message.patient_name) {
                            let patient_name = r.message.patient_name;
                            let name_parts = patient_name.split(' ');

                            if (name_parts.length === 2) {
                                frm.set_value('first_name', name_parts[0]);
                                frm.set_value('last_name', name_parts[1]);
                                frm.set_value('middle_name', '');
                            } else if (name_parts.length === 3) {
                                frm.set_value('first_name', name_parts[0]);
                                frm.set_value('middle_name', name_parts[1]);
                                frm.set_value('last_name', name_parts[2]);
                            } else if (name_parts.length > 3) {
                                frm.set_value('first_name', name_parts[0]);
                                frm.set_value('last_name', name_parts[name_parts.length - 1]);
                                frm.set_value('middle_name', name_parts.slice(1, -1).join(' '));
                            } else {
                                frm.set_value('first_name', patient_name);
                                frm.set_value('middle_name', '');
                                frm.set_value('last_name', '');
                            }
                        }
                    });
            }
        };

        const dob = document.querySelector("input[data-fieldname='dob']");
        const referenceNode = dob;
        if (!document.querySelector('#ageInputControl')) {
            const newNode = document.createElement('div');
            newNode.setAttribute('id', 'ageInputControl');
            newNode.style = 'display:flex;flex-flow:row wrap;justify-content: space-around';
            newNode.innerHTML = `
                <label style='width:25%;' class='control-label' style='padding-right: 0px;'>Day</label>
                <label style='width:25%;' class='control-label' style='padding-right: 0px;'>Month</label>
                <label style='width:25%;' class='control-label' style='padding-right: 0px;'>Age</label>
                <label style='width:25%;' class='control-label' style='padding-right: 0px;'>Year</label>
                <br>
                <input style='width:25%;' id='dob-day' type='number' placeholder='1' min='1' max='31' class='input-with-feedback form-control bold'></input>
                <input style='width:25%;' id='dob-mon' type='number' placeholder='1' min='1' max='12' class='input-with-feedback form-control bold'></input>
                <input style='width:25%;' id='dob-age' type='number' placeholder='0' class='input-with-feedback form-control bold'></input>
                <input style='width:25%;' id='dob-year' type='number' placeholder='0' class='input-with-feedback form-control bold'></input>
                <br><br>`;
            referenceNode.parentNode.insertBefore(newNode, referenceNode);

            let dv = 1, mv = 1, av = 0, yv = 1000;

            let setdob = (useY) => {
                dv.toString().length == 1 && (dv = '0' + dv);
                mv.toString().length == 1 && (mv = '0' + mv);
                let dobv = `${useY ? yv : new Date().getFullYear() - av}-${mv}-${dv}`;
                frm.set_value('dob', dobv);
                tooltip();
            };

            function tooltip() {}

            let iday = document.querySelector('#dob-day');
            iday.onchange = dayChange;
            iday.onfocuschange = dayChange;

            function dayChange() {
                dv = Math.abs((this.value || 1));
                dv > 31 && (dv = 31);
                dv < 1 && (dv = 1);
                dv = parseInt(dv);
                this.value = dv;
                setdob();
            }

            let imonth = document.querySelector('#dob-mon');
            imonth.onchange = monthChange;
            imonth.onfocuschange = monthChange;

            function monthChange() {
                mv = Math.abs((this.value || 1));
                mv > 12 && (mv = 12);
                mv < 1 && (mv = 1);
                mv = parseInt(mv);
                this.value = mv;
                setdob();
            }

            let iyear;
            let iage = document.querySelector('#dob-age');
            iage.onchange = ageChange;
            iage.onfocuschange = ageChange;

            function ageChange() {
                av = Math.abs(parseInt((this.value || 0)));
                av < 0 && (av = 0);
                av > 200 && (av = 200);
                this.value = av;
                iyear.value = new Date().getFullYear() - av;
                setdob();
            }

            iyear = document.querySelector('#dob-year');
            iyear.onchange = yChange;
            iyear.onfocuschange = yChange;

            function yChange() {
                yv = Math.abs((this.value || 1900));
                yv > new Date().getFullYear() && (yv = new Date().getFullYear());
                yv < 1900 && (yv = 1900);
                yv = parseInt(yv);
                this.value = yv;
                iage.value = new Date().getFullYear() - yv;
                setdob(true);
            }

            function setAgeValues(full_age) {
                av = full_age;
                dv = 1;
                mv = 1;
                yv = new Date().getFullYear() - av;
                iyear.value = yv;
                iage.value = av;
                setdob(true);
            }

            function age_html() {
                let cal = document.querySelector(`[data-fieldname='age_html']`);
                let diff = frappe.datetime.get_diff(frappe.datetime.get_today(), `${new Date().getFullYear() - (iage.value || 0)}\\${mv}\\${dv}`);
                let yrs = 0;
            }
        }

        var consultation_item = "Consultation";

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Item',
                filters: { item_group: consultation_item },
                limit: 1
            },
            callback: function(response) {
                if (response.message && response.message.length > 0) {
                    frm.set_query('custom_consultation', function() {
                        return {
                            filters: { item_group: consultation_item }
                        };
                    });
                }
            }
        });
    },
    custom_consultation: function(frm) {
        if (frm.doc.custom_consultation) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Item Price',
                    filters: {
                        item_code: frm.doc.custom_consultation,
                        price_list: 'Standard Selling',
                        selling: 1
                    },
                    fieldname: 'price_list_rate'
                },
                callback: function(response) {
                    if (response.message) {
                        frm.set_value('custom_fee', response.message.price_list_rate);
                    }
                }
            });
        }
    }
});
