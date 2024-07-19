frappe.ui.form.on('Material Request Item', {
    from_warehouse: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Clear the fields
        frappe.model.set_value(cdt, cdn, 'custom_actual_qty_swarehouse', null);
        frappe.model.set_value(cdt, cdn, 'custom_average_consuption', null);

        if (row.item_code && row.from_warehouse) {
            frappe.call({
                method: 'hmh_custom_app.custom_api.material_request.get_actual_qty',  // Replace with your actual path
                args: {
                    item_code: row.item_code,
                    warehouse: row.from_warehouse
                },
                callback: function(r) {
                    // console.log(r.message)
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_actual_qty_swarehouse', r.message);
                    }
                }
            });

            frappe.call({
                method: 'hmh_custom_app.custom_api.material_request.get_average_consumption',  // Replace with your actual path
                args: {
                    item_code: row.item_code,
                    warehouse: row.warehouse
                },
                callback: function(r) {
                    console.log(r.message)
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_average_consuption', r.message);
                    }
                }
            });
        }
    },
    warehouse: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Clear the fields
        frappe.model.set_value(cdt, cdn, 'custom_actual_qty_swarehouse', null);
        frappe.model.set_value(cdt, cdn, 'custom_average_consuption', null);

        if (row.item_code && row.from_warehouse) {
            frappe.call({
                method: 'hmh_custom_app.custom_api.material_request.get_actual_qty',  // Replace with your actual path
                args: {
                    item_code: row.item_code,
                    warehouse: row.from_warehouse
                },
                callback: function(r) {
                    // console.log(r.message)
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_actual_qty_swarehouse', r.message);
                    }
                }
            });

            frappe.call({
                method: 'hmh_custom_app.custom_api.material_request.get_average_consumption',  // Replace with your actual path
                args: {
                    item_code: row.item_code,
                    warehouse: row.warehouse
                },
                callback: function(r) {
                    console.log(r.message)
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_average_consuption', r.message);
                    }
                }
            });
        }
    }
});
