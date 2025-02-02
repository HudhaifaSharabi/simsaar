import requests
import frappe
from frappe.model.document import Document
from frappe import _

API_URL = "http://localhost:3000"
API_KEY = frappe.conf.get("whatsapp_api_key") or "3b3e2b363e7dc6544fc833672d7f3207fa814842bce4c42b986d671552379f4f"
class WhatsAppMessage(Document):
    def before_save(self):
        if not hasattr(self, 'type'):
            self.type = 'Outgoing'  # Default value for type
        if not hasattr(self, 'reference_doctype'):
            self.reference_doctype = '' 
        if not hasattr(self, 'reference_name'):
            self.reference_name = '' 
    # def after_insert(self):
    #     url = "http://localhost:3000/send-message"
    #     payload = {
    #         "number": self.recipient_number,  # Field in WhatsApp Message DocType
    #         "message": self.message    # Field in WhatsApp Message DocType
    #     }
    #     response = requests.post(url, json=payload)
    #     if response.status_code == 200:
    #         frappe.msgprint("Message sent successfully!")
    #     else:
    #         frappe.throw("Failed to send message.")
# @frappe.whitelist()
# def send_whatsapp_message(docname):
#     url = "http://localhost:3000/send-message"
#     payload = {
#         "number": "00967778919884",  # Field in WhatsApp Message DocType
#         "message": "hi"    # Field in WhatsApp Message DocType
#     }
#     response = requests.post(url, json=payload)
#     if response.status_code == 200:
#         frappe.msgprint("Message sent successfully!")
#     else:
#         frappe.throw("Failed to send message.")

#     doc = frappe.get_doc("WhatsApp Message", docname)
#     doc.save()
#     frappe.db.commit()

@frappe.whitelist()
def send_whatsapp_message(doc):
  doc = frappe.parse_json(doc)
  try:
    response = requests.post(
      f"{API_URL}/send-message",
      headers={"X-API-Key": API_KEY},
      json={"phone": doc.recipient, "message": doc.message}
    )
    return response.json()
  except Exception as e:
    frappe.log_error(_("Failed to send message"), e)
    return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_qr_code():
  try:
    response = requests.get(
      f"{API_URL}/qr",
      headers={"X-API-Key": API_KEY}
    )
    return response.json()
  except Exception as e:
    frappe.log_error(_("Failed to fetch QR code"), e)
    return {"error": str(e)}

@frappe.whitelist()
def get_session_status():
  try:
    response = requests.get(
      f"{API_URL}/qr",
      headers={"X-API-Key": API_KEY}
    )
    data = response.json()
    return {"status": "Connected" if data.get("authenticated") else "Authenticating"}
  except:
    return {"status": "Disconnected"}