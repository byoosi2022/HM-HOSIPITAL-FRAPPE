frappe.ui.form.on('Material Request', {
    set_from_warehouse: function(frm) {
        update_custom_fields(frm);
    },
    set_warehouse: function(frm) {
        update_custom_fields(frm);
    }
});

frappe.ui.form.on('Material Request Item', {
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code && row.warehouse) {
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
                    
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_average_consumption', r.message);
                    }
                }
            });
        }
    }
});




function update_custom_fields(frm) {
    frm.doc.items.forEach(function(item) {
        if (item.item_code && frm.doc.set_from_warehous) {
            frappe.call({
                method: 'hmh_custom_app.custom_api.material_request.get_actual_qty',
                args: {
                    item_code: item.item_code,
                    warehouse: frm.doc.set_from_warehouse
                },
                callback: function(r) {
                    console.log("set_from_warehouse");
                    if (r.message !== undefined) {
                        frappe.model.set_value(item.doctype, item.name, 'custom_actual_qty_swarehouse', r.message);
                    }
                }
            });

            frappe.call({
                method: 'hmh_custom_app.custom_api.material_request.get_average_consumption',
                args: {
                    item_code: item.item_code,
                    warehouse: frm.doc.set_from_warehouse
                },
                callback: function(r) {
                    console.log("set_warehouse");
                    if (r.message !== undefined) {
                        frappe.model.set_value(item.doctype, item.name, 'custom_average_consuption', r.message);
                    }
                }
            });
        }
    });
}

