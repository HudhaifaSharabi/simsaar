// Copyright (c) 2025, hudhaifa alsharabi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WhatsApp Settings", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("WhatsApp Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__("Start Session"), () => {
            frappe.call({
                method: "simsaar.simsaar.utils.whatsapp.initialize_whatsapp_session",
                callback: () => frm.reload_doc()
            });
        });
    }
});