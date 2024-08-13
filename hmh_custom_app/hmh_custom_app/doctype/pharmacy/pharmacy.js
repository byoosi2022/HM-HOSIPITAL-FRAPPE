// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Pharmacy", {
//     refresh(frm) {
//         // You can add additional refresh logic here if needed
//     },
// });

frappe.ui.form.on('Pharmacy Items', {
    amount: function (frm, cdt, cdn) {
        calculateTotalsPharmacy(frm);
    },
    qty: function (frm, cdt, cdn) {
        calculateTotalsPharmacy(frm);
    },
    rate: function (frm, cdt, cdn) {
        calculateTotalsPharmacy(frm);
    }
});

function calculateTotalsPharmacy(frm) {
    var total_qty = 0;
    var total_amount = 0;

    frm.doc.drug_prescription.forEach(function (item) {
        // Calculate the amount for each item
        item.amount = item.qty * item.rate;
        total_qty += item.qty;
        total_amount += item.amount;
    });

    // Set the calculated totals in the form
    frm.set_value('total_qty', total_qty);
    frm.set_value('total_amount', total_amount);
    refresh_field('drug_prescription');
}
