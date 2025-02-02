# simsaar/simsaar/utils/whatsapp.py
import frappe
import qrcode
import time
from playwright.sync_api import sync_playwright
from frappe.utils import get_site_path

@frappe.whitelist()
def initialize_whatsapp_session():
    settings = frappe.get_doc("WhatsApp Settings", "WhatsApp Settings")
    browser = None
    
    try:
        with sync_playwright() as p:
            # Configure browser for headless operation
            browser = p.chromium.launch(
                headless=True,  # Essential for server environments
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ],
                timeout=60000  # Increased launch timeout
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            
            # Enhanced navigation with retries
            for attempt in range(3):
                try:
                    page.goto(
                        "https://web.whatsapp.com",
                        wait_until="networkidle",
                        timeout=120000
                    )
                    break
                except Exception as nav_error:
                    if attempt == 2:
                        raise nav_error
                    time.sleep(5)
                    continue

            # QR code handling
            qr_selector = "div[data-ref]"
            try:
                page.wait_for_selector(qr_selector, state="visible", timeout=90000)
            except Exception as qr_error:
                frappe.log_error(f"QR Code Detection Failed: {str(qr_error)}")
                raise

            qr_data = page.locator(qr_selector).get_attribute("data-ref")
            qr_img = qrcode.make(qr_data)
            qr_path = get_site_path("public", "files", "whatsapp_qr.png")
            qr_img.save(qr_path)

            # Document handling with version control
            with frappe.db.transaction():
                settings.reload()
                settings.qr_code = f"/files/whatsapp_qr.png"
                settings.session_status = "Waiting for Scan"
                settings.save(ignore_version=True)
                frappe.db.commit()

            # Session monitoring
            start_time = time.time()
            while time.time() - start_time < 300:  # 5 minute timeout
                if page.query_selector("div[title='New chat']"):
                    with frappe.db.transaction():
                        settings.reload()
                        settings.session_status = "Active"
                        settings.save(ignore_version=True)
                        frappe.db.commit()
                    frappe.cache().set_value("whatsapp_context", context)
                    return {"status": "success"}
                time.sleep(5)

            frappe.throw("QR scan timeout. Please try again.")

    except Exception as e:
        error_msg = f"WhatsApp Init Error: {str(e)}"
        frappe.log_error(error_msg)
        handle_failure(settings)
        return {"status": "error", "message": error_msg}
    finally:
        if browser:
            browser.close()

def handle_failure(settings):
    try:
        settings.reload()
        settings.session_status = "Inactive"
        settings.save(ignore_version=True)
        frappe.db.commit()
    except Exception as save_error:
        frappe.log_error(f"Failure State Save Error: {str(save_error)}")

@frappe.whitelist()
def send_queued_messages():
    context = frappe.cache().get_value("whatsapp_context")
    if not context:
        return {"status": "error", "message": "No active WhatsApp session"}

    queued_messages = frappe.get_all("WhatsApp Message",
        filters={"status": "Queued"},
        fields=["name", "recipient", "message"]
    )

    results = []
    for msg in queued_messages:
        try:
            doc = frappe.get_doc("WhatsApp Message", msg.name)
            result = send_single_message(context, doc.recipient, doc.message)
            doc.status = "Sent" if result["success"] else "Failed"
            results.append(result)
        except Exception as e:
            frappe.log_error(f"Message Processing Error: {str(e)}")
            results.append({"name": msg.name, "status": "error", "message": str(e)})
        finally:
            doc.save(ignore_permissions=True)
    
    return {"results": results}

def send_single_message(context, recipient, message):
    page = context.new_page()
    try:
        page.goto(
            f"https://web.whatsapp.com/send?phone={recipient}",
            wait_until="networkidle",
            timeout=60000
        )
        
        # Enhanced message input handling
        input_selector = "div[title='Type a message']"
        page.wait_for_selector(input_selector, timeout=30000)
        
        # Type message in chunks to avoid detection
        for chunk in [message[i:i+50] for i in range(0, len(message), 50)]:
            page.keyboard.type(chunk, delay=50)
            time.sleep(0.2)
        
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3)  # Wait for send confirmation
        
        return {"success": True, "name": recipient}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        page.close()