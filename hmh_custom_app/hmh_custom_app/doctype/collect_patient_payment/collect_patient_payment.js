// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Collect Patient Payment", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Collect Patient Payment', {
    refresh: function(frm) {
        // Function to create sales invoice
        function createSalesInvoice() {
            frappe.call({
                method: "hmh_custom_app.custom_api.sales_invoice.create_sales_invoice_payments",
                args: {
                    patient_payment: frm.doc.name
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(response.message);
                    } else if (response.error) {
                        frappe.msgprint(__('Error: ') + response.error);
                    } else {
                        frappe.msgprint(__('Failed to create Sales Invoice.'));
                    }
                },
                error: function(error) {
                    frappe.msgprint(__('There was an error creating the Sales Invoice.'));
                    console.error(error);
                }
            });
        }

        // Show/hide "Bill Now" or "Bill Later" button based on customer_group and bill_status fields
        function toggleBillButton() {
            var showBillNow = true;

            if (frm.doc.customer_group === "Insurance" || frm.doc.bill_status === "CLOSED") {
                showBillNow = false;
            }

            // Clear previous actions
            frm.page.clear_actions_menu();

            if (frm.doc.bill_status !== "CLOSED") {
                if (showBillNow) {
                    frm.page.set_primary_action(__('Bill Now'), function() {
                        createSalesInvoice();
                    }, 'bill_now_button');
                } else {
                    frm.page.set_primary_action(__('Bill Later'), function() {
                        createSalesInvoice();
                    }, 'bill_later_button');
                }

                frm.toggle_display(['bill_now_button'], showBillNow);
                frm.toggle_display(['bill_later_button'], !showBillNow);
            } else {
                frm.toggle_display(['bill_now_button', 'bill_later_button'], false);
            }

            // Reset the "Save" button action
            // frm.page.set_secondary_action(__('Save'), function() {
            //     frm.save();
            // });
        }

        // Call toggleBillButton on form load and on customer_group or bill_status field change
        toggleBillButton();
        frm.fields_dict.customer_group.$input.on('change', function() {
            toggleBillButton();
        });
        frm.fields_dict.bill_status.$input.on('change', function() {
            toggleBillButton();
        });
    },
    cash: function(frm) {
        // Toggle visibility of 'paid_amount_cash' field based on 'cash' checkbox
        frm.toggle_display('paid_amount_cash', frm.doc.cash);
    },
    mtn_mobile_money: function(frm) {
        // Toggle visibility of 'paid_amount_mm' and 'transaction_mtn' fields based on 'mtn_mobile_money' checkbox
        frm.toggle_display('paid_amount_mm', frm.doc.mtn_mobile_money);
        frm.toggle_display('transaction_mtn', frm.doc.mtn_mobile_money);
    },
    paid_amount_amm: function(frm) {
        // Toggle visibility of 'paid_amount_airtel' and 'transaction_airtel' fields based on 'paid_amount_amm' checkbox
        frm.toggle_display('paid_amount_airtel', frm.doc.paid_amount_amm);
        frm.toggle_display('transaction_airtel', frm.doc.paid_amount_amm);
    },
    posting_date: function (frm) {
        // Calculate the due date as posting date + 30 days
        var postingDate = new Date(frm.doc.posting_date);
        var dueDate = new Date(postingDate.setDate(postingDate.getDate() + 30));

        // Format due date as YYYY-MM-DD
        var formattedDueDate = dueDate.toISOString().split('T')[0];

        // Set the due date in the form
        frm.set_value('due_date', formattedDueDate);
    },
});


frappe.ui.form.on('Payment Items', {
    amount: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    },
    qty: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    },

    item_code: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
        fetch_price(frm);
    }
});

function calculateTotalsTransfers(frm) {
    frm.set_value('grand_totals', "");
    frm.set_value('total_qty', "");
    var total_amount = 0;
    var total_qty = 0;
    frm.doc.items.forEach(function (item) {
        item.amount = item.rate * item.qty;
        total_amount += item.amount;
        total_qty += item.qty;
    });
    frm.set_value('grand_totals', total_amount);
    frm.set_value('total_qty', total_qty);
    refresh_field('items');
}
function fetch_price(frm) {
    frm.doc.items.forEach(function (item) {
        frappe.call({
            method: "hmh_custom_app.custom_api.fetch_item_price.fetch_item_rate",
            args: {
                item_code: item.item_code,
                price_list: frm.doc.price_list
            },
            callback: function(response) {
                if (response.message) {
                    frappe.model.set_value(item.doctype, item.name, 'rate', response.message);
                }
            }
        });
    });
}




