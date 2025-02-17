import frappe
from frappe.auth import LoginManager
from frappe import _
from datetime import datetime
import random



@frappe.whitelist(allow_guest=True)
def signup(email, name, password, phone, gender):
    if not frappe.db.exists("User", email):
        # Create the user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": name,
            "enabled": 1,
            "new_password": password,
            "gender": gender,
            "mobile_no": phone,
            "user_type": "Website User"
        })
        user.insert(ignore_permissions=True)

        # Log the user in after signup
        login_manager = LoginManager()
        login_manager.authenticate(user=email, pwd=password)
        login_manager.post_login()

        # Set cookies for the session
        frappe.local.response["cookie"] = {
            "sid": frappe.session.sid,
            "expires": None,
            "path": "/",
            "httponly": True,
        }

        return {"message": "User created and logged in successfully"}
    else:
        frappe.throw("Email already registered.")



@frappe.whitelist(allow_guest=True)
def booking(number_of_rooms, room_type, type, check_in_date, check_out_date, gust_number, child_number, guest_name=None, mobile_number=None):
    # Convert check-in and check-out dates to MySQL format (YYYY-MM-DD)
    try:
        check_in_date = datetime.strptime(check_in_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        check_out_date = datetime.strptime(check_out_date, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Please use DD-MM-YYYY."}

    # Check if user is logged in or a guest
    if frappe.session.user and frappe.session.user != "Guest":
        # Fetch user details from Frappe database
        user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or guest_name
        user_mobile_number = frappe.db.get_value("User", frappe.session.user, "mobile_no") or mobile_number
    else:
        # Use guest data
        user_full_name = guest_name
        user_mobile_number = mobile_number

        # Ensure guest provided required details
        if not user_full_name or not user_mobile_number:
            return {"error": "Guest users must provide guest_name and mobile_number."}

    # Create the booking document
    booking_doc = frappe.get_doc({
        "doctype": "Booking",
        "number_of_rooms": number_of_rooms,
        "guest_name": user_full_name,  
        "user_name": frappe.session.user if frappe.session.user != "Guest" else None,
        "mobile_number": user_mobile_number,
        "room_type": room_type,
        "type": type,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "gust_number": gust_number,
        "child_number": child_number
    })
    booking_doc.insert(ignore_permissions=True)

    return {"message": "Booking created successfully", "guest_name": user_full_name}


@frappe.whitelist(allow_guest=True)
def get_all_facilities_surroundings(status, facilitie):
    """Fetch all Facilities Surroundings with child table (table_nnki)."""
    facilities = frappe.get_all("Facilities Surroundings", fields=["*"], filters={"status": status, "facilitie": facilitie})

    for facility in facilities:
        # Fetch child table data (Surroundings)
        facility["sub_surroundings"] = frappe.get_all(
            "Surroundings",
            filters={"parent": facility["name"]}, 
            fields=["*"]
        )

    return facilities

# @frappe.whitelist(allow_guest=True)
# def send_otp(phone_number):
#     """
#     Generate OTP, send via WhatsApp, and store it for verification.
#     """
#     try:
#         if not phone_number:
#             return {"success": False, "error": "Phone number is required"}

#         # Generate a random 4-digit OTP
#         otp = str(random.randint(1000, 9999))

#         # Store OTP in the database (temporary storage)
#         otp_entry = frappe.get_doc({
#             "doctype": "OTP Verification",
#             "phone_number": phone_number,
#             "otp": otp
#         })
#         otp_entry.insert(ignore_permissions=True)
#         frappe.db.commit()

#         # Send OTP via WhatsApp
#         message = f"رمز التحقق الخاص بك هو: {otp}"
#         response = frappe.call(
#             "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
#             recipient=phone_number,
#             message=message
#         )

#         return {"success": True, "message": "OTP sent successfully"}
    
#     except Exception as e:
#         frappe.log_error(f"WhatsApp API Error: {str(e)}")
#         return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
def send_otp(phone_number):
    """
    Generate OTP, send via WhatsApp, and store it temporarily.
    """
    try:
        if not phone_number:
            return {"success": False, "error": "Phone number is required"}

        # Generate OTP
        frappe.cache.delete_value(f"otp_{phone_number}") # `frappe.cache.hdel` if using hashes.

        otp = str(random.randint(1000, 9999))
        frappe.cache.set_value(f"otp_{phone_number}", otp, expires_in_sec=60)  # Store OTP for 5 minutes

        # Send OTP via WhatsApp
        default_message = f"رمز التحقق: {otp}"
        frappe.call(
            "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
            recipient=phone_number,
            message=default_message
        )

        return {"success": True, "message": "OTP sent successfully"}

    except Exception as e:
        frappe.log_error(f"OTP Error: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
def verify_otp(phone_number, otp):
    try:
        stored_otp = frappe.cache.get_value(f"otp_{phone_number}")
        if not stored_otp or stored_otp != otp:
            return {"success": False, "error": "Invalid OTP"}

        # Check if user exists by phone number
        user_id = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
        if not user_id:
            return {"success": False, "error": "User not found. Please complete registration."}
        user_doc = frappe.get_doc("User", user_id)
        mobile_no = user_doc.mobile_no
        first_name = user_doc.first_name
        gender = user_doc.gender
        birth_date = user_doc.birth_date

        # Manually log in the user by setting session
        try:
            frappe.local.login_manager.user = user_id
            frappe.local.login_manager.post_login()
            frappe.log_error(f"User {user_id} logged in successfully.")
        except Exception as e:
            frappe.log_error(f"Login Error: {str(e)}")
            return {"success": False, "error": f"Login failed: {str(e)}"}

        # login_manager = LoginManager()
        # login_manager.authenticate(user=user_id, pwd=ىخىث)  # No password needed
        # login_manager.post_login()

        # Return session ID instead of setting a cookie
        return {
            "success": True,
            "message": "Login successful",
            "user_id": user_id,
            "mobile_no": mobile_no,
            "first_name":first_name,
            "gender":gender,
            "birth_date":birth_date,
            "sid": frappe.session.sid  # Send session ID to Flutter
        }


    except Exception as e:
        frappe.log_error(f"Login Error: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
def register_user(phone_number, full_name, gender=None, birth_date=None):
    """
    Create a new user and log them in.
    """
    try:
        # التحقق مما إذا كان المستخدم مسجلاً بالفعل
        existing_user = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
        if existing_user:
            return {"success": False, "error": "User already exists."}

        # إنشاء بريد إلكتروني افتراضي لتجنب الأخطاء
        fake_email = f"user_{phone_number}@simsaarerp.net"

        # إنشاء مستخدم جديد
        new_user = frappe.get_doc({
            "doctype": "User",
            "first_name": full_name,
            "mobile_no": phone_number,
            "email": fake_email,
            "birth_date":birth_date,
            "gender":gender,
            "username": phone_number,  # تجنب الخطأ بإضافة بريد إلكتروني افتراضي
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0,
            
        })
        new_user.insert(ignore_permissions=True)

        # تسجيل دخول المستخدم الجديد
        frappe.local.login_manager = LoginManager()
        try:
            frappe.local.login_manager.user = new_user.name
            frappe.local.login_manager.post_login()
            frappe.log_error(f"User {new_user.name} logged in successfully.")
        except Exception as e:
            frappe.log_error(f"Login Error: {str(e)}")
            return {"success": False, "error": f"Login failed: {str(e)}"}

        return {
            "success": True,
            "message": "User registered and logged in successfully",
            "user_id": new_user.name,
            "mobile_no": new_user.mobile_no,
            "first_name":new_user.first_name,
            "gender":new_user.gender,
            "birth_date":new_user.birth_date,
            "sid": frappe.session.sid  # إرسال session ID لاستخدامه في Flutter
        }

    except Exception as e:
        frappe.log_error(f"Registration Error: {str(e)}")
        return {"success": False, "error": str(e)}
