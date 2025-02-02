// Copyright (c) 2025, hudhaifa alsharabi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WhatsApp Message", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('WhatsApp Message', {
    // before_save: function(frm) {
    //     frappe.call({
    //         method: 'simsaar.simsaar.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message',
    //         args: {
    //             docname: frm.doc.name
    //         },
    //         callback: function(r) {
    //             frm.reload_doc();
    //             frappe.msgprint(__('Message sent successfully!'));
    //         }
    //     });
    // }
    refresh(frm) {
        frm.add_custom_button(__('Send Message'), () => {
          frappe.call({
            method: 'simsaar.simsaar.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message',
            args: { doc: frm.doc },
            callback: (r) => {
              if (r.message.success) {
                frappe.show_alert({ message: __('Message sent!'), indicator: 'green' });
                frm.reload_doc();
              }
            }
          });
        });
      }
});

