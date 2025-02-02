// Copyright (c) 2025, hudhaifa alsharabi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WhatsApp Session", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('WhatsApp Session', {
//     refresh: function(frm) {
//         // Connect to Node.js server
//         const socket = io.connect('http://localhost:3000');

//         socket.on('qr', function(qr) {
//             frm.set_value('status', 'Scan the QR Code');
//             frm.fields_dict.qr_code.$wrapper.html('');
//             new QRCode(frm.fields_dict.qr_code.$wrapper[0], qr);
//         });

//         socket.on('authenticated', function() {
//             frm.set_value('status', 'Authenticated');
//             frm.refresh();
//         });

//         socket.on('ready', function() {
//             frm.set_value('status', 'WhatsApp Ready');
//             frm.refresh();
//         });
//     }
// });
frappe.ui.form.on('WhatsApp Session', {
    refresh(frm) {
      // Show QR code and status
      if (frm.doc.status !== 'Connected') {
        frm.add_custom_button(__('Start WhatsApp Session'), () => {
          frm.set_value('status', 'Authenticating');
          fetchQRCode(frm);
        });
      }
  
      // Auto-refresh status every 5 seconds
      if (!frm.qrInterval) {
        frm.qrInterval = setInterval(() => checkStatus(frm), 5000);
      }
    },
  
    before_close(frm) {
      clearInterval(frm.qrInterval);
    }
  });
  
  function fetchQRCode(frm) {

    frappe.call({
    method: 'simsaar.simsaar.doctype.whatsapp_message.whatsapp_message.get_qr_code',
      callback: (response) => {
        if (response.message.qr) {
          frm.set_df_property('qr_code', 'options', `
            <div style="text-align: center;">
              <img src="${response.message.qr}" width="200" />
              <p>Scan this QR code with WhatsApp</p>
            </div>
          `);
        }
      }
    });
  }
  
  function checkStatus(frm) {
    frappe.call({
      method: 'simsaar.simsaar.doctype.whatsapp_message.whatsapp_message.get_session_status',
      callback: (response) => {
        frm.set_value('status', response.message.status);
        if (response.message.status === 'Connected') {
          clearInterval(frm.qrInterval);
            
        }
      }
    });
  }