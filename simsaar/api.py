import frappe
from frappe.auth import LoginManager
from frappe import _
from frappe.utils import now_datetime

from datetime import datetime, timedelta
import random
from frappe.core.doctype.user.user import generate_keys
import traceback
# import jwt
# import hmac
import base64
from frappe.integrations.oauth2 import get_token
from frappe.sessions import Session

# SECRET_KEY = frappe.get_site_config().get("jwt_secret")

# @frappe.whitelist(allow_guest=True)
# def signup(email, name, password, phone, gender):
#     if not frappe.db.exists("User", email):
#         # Create the user
#         user = frappe.get_doc({
#             "doctype": "User",
#             "email": email,
#             "first_name": name,
#             "enabled": 1,
#             "new_password": password,
#             "gender": gender,
#             "mobile_no": phone,
#             "user_type": "Website User"
#         })
#         user.insert(ignore_permissions=True)

#         # Log the user in after signup
#         login_manager = LoginManager()
#         login_manager.authenticate(user=email, pwd=password)
#         login_manager.post_login()

#         # Set cookies for the session
#         frappe.local.response["cookie"] = {
#             "sid": frappe.session.sid,
#             "expires": None,
#             "path": "/",
#             "httponly": True,
#         }

#         return {"message": "User created and logged in successfully"}
#     else:
#         frappe.throw("Email already registered.")




# @frappe.whitelist(methods=["POST"])  # Only allow authenticated users
# def booking(number_of_rooms, room_type, type, check_in_date, check_out_date, gust_number, child_number, places_prices):
#     try:
#         # ✅ Support API authentication
#         auth_header = frappe.get_request_header("Authorization")

#         if not auth_header or "token" not in auth_header:
#             return {"error": "Authorization header missing or incorrect format."}

#         # ✅ Extract API Key and Secret
#         try:
#             _, credentials = auth_header.split(" ", 1)  # Extract after "token"
#             api_key, api_secret = credentials.split(":")
#         except ValueError:
#             return {"error": "Invalid API token format. Expected 'token api_key:api_secret'"}

#         # ✅ Validate API Key in Database
#         user_email = frappe.db.get_value("User", {"api_key": api_key}, "name")
#         stored_secret = frappe.utils.password.get_decrypted_password("User", user_email, "api_secret")

#         if not user_email or stored_secret != api_secret:
#             return {"error": "Invalid API credentials."}


#         # ✅ Fetch user details
#         user_doc = frappe.get_doc("User", user_email)
#         user_full_name = user_doc.full_name
#         user_mobile_number = user_doc.mobile_no

#         # ✅ Prevent duplicate bookings
#         # existing_booking = frappe.db.exists("Booking", {"user": user, "check_in_date": check_in_date, "check_out_date": check_out_date})
#         # if existing_booking:
#         #     return {"error": "You already have a booking for these dates."}

#         # ✅ Create the booking document
#         booking_doc = frappe.get_doc({
#             "doctype": "Booking",
#             "number_of_rooms": number_of_rooms,
#             "guest_name": user_full_name,
#             "user": user_email,  
#             "mobile_number": user_mobile_number,
#             "room_type": room_type,
#             "type": type,
#             "check_in_date": check_in_date,
#             "check_out_date": check_out_date,
#             "gust_number": gust_number,
#             "child_number": child_number,
#             "places_prices": places_prices
#         })
#         booking_doc.insert(ignore_permissions=True)

#         # # ✅ Prepare WhatsApp notification
#         # booking_message = f"""
#         # 🏨 *حجز جديد*
#         # 🔹 *اسم العميل:* {user_full_name}
#         # 📱 *رقم الهاتف:* {user_mobile_number}
#         # 📅 *تسجيل الدخول:* {check_in_date}
#         # 📅 *تسجيل الخروج:* {check_out_date}
#         # 🛏️ *عدد الغرف:* {number_of_rooms}
#         # 👤 *عدد الضيوف:* {gust_number} | 👶 *أطفال:* {child_number}
#         # 💰 *السعر الإجمالي:* {places_prices}  
#         # """

#         # ✅ List of admin phone numbers to notify
#         # admin_phone_numbers = [ "967778919884"]
#                 # admin_phone_numbers = ["967773552355", "967778919884"]

#         # for phone_number in admin_phone_numbers:
#         #     try:
#         #         frappe.call(
#         #             "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
#         #             recipient=phone_number,
#         #             message=booking_message
#         #         )
#         #     except Exception as e:
#         #         frappe.log_error(f"WhatsApp message failed: {str(e)}")

#         return {
#             "success": True,
#             "message": "Booking created successfully",
#             "booking_id": booking_doc.name,  
#             "guest_name": user_full_name
#         }

#     except Exception as e:
#         frappe.log_error(f"Booking Error: {str(e)}")
#         return {"success": False, "error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=["POST"])
# def booking(number_of_rooms, room_type, type, check_in_date, check_out_date, gust_number, child_number, places_prices):
#     user = authenticate_request()

#     # ✅ Create the booking document
#     booking_doc = frappe.get_doc({
#         "doctype": "Booking",
#         "user": user,
#         "number_of_rooms": number_of_rooms,
#         "room_type": room_type,
#         "type": type,
#         "check_in_date": check_in_date,
#         "check_out_date": check_out_date,
#         "gust_number": gust_number,
#         "child_number": child_number,
#         "places_prices": places_prices
#     })
#     booking_doc.insert(ignore_permissions=True)

#     return {
#         "success": True,
#         "message": "Booking created successfully",
#         "booking_id": booking_doc.name
#     }
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
#1
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
# 2
# @frappe.whitelist(allow_guest=True)
# def send_otp(phone_number):
#     """
#     Generate OTP, send via WhatsApp, and store it temporarily.
#     """
#     try:
#         if not phone_number:
#             return {"success": False, "error": "Phone number is required"}

#         # Generate OTP
#         frappe.cache.delete_value(f"otp_{phone_number}") # `frappe.cache.hdel` if using hashes.

#         otp = str(random.randint(1000, 9999))
#         frappe.cache.set_value(f"otp_{phone_number}", otp, expires_in_sec=60)  # Store OTP for 5 minutes

#         # Send OTP via WhatsApp
#         default_message = f"رمز التحقق: {otp}"
#         frappe.call(
#             "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
#             recipient=phone_number,
#             message=default_message
#         )

#         return {"success": True, "message": "OTP sent successfully"}

#     except Exception as e:
#         frappe.log_error(f"OTP Error: {str(e)}")
#         return {"success": False, "error": str(e)}



@frappe.whitelist(allow_guest=True)
def send_otp(phone_number):
    """
    توليد رمز OTP وإرساله عبر WhatsApp وتخزينه مؤقتًا.
    """
    try:
        if not phone_number:
            return {"success": False, "error": "رقم الهاتف مطلوب"}

        # حذف أي رمز قديم
        frappe.cache().delete_value(f"otp_{phone_number}")

        # توليد OTP جديد
        otp = str(random.randint(1000, 9999))
        frappe.cache.set_value(f"otp_{phone_number}", otp, expires_in_sec=300)  # تخزين لـ 5 دقائق

        # إرسال OTP عبر WhatsApp
        default_message = f"رمز التحقق الخاص بك هو: {otp}"
        frappe.call(
            "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
            recipient=phone_number,
            message=default_message
        )

        return {"success": True, "message": "تم إرسال رمز التحقق بنجاح" , "otp": otp}

    except Exception as e:
        frappe.log_error(f"OTP Error: {str(e)}")
        return {"success": False, "error": str(e)}

# 1
# @frappe.whitelist(allow_guest=True)
# def verify_otp(phone_number, otp):
#     try:
#         stored_otp = frappe.cache.get_value(f"otp_{phone_number}")
#         if not stored_otp or stored_otp != otp:
#             return {"success": False, "error": "Invalid OTP"}

#         # Check if user exists by phone number
#         user_id = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
#         if not user_id:
#             return {"success": False, "error": "User not found. Please complete registration."}
#         user_doc = frappe.get_doc("User", user_id)
#         mobile_no = user_doc.mobile_no
#         first_name = user_doc.first_name
#         gender = user_doc.gender
#         birth_date = user_doc.birth_date

#         # Manually log in the user by setting session
#         try:
#             frappe.local.login_manager.user = user_id
#             frappe.local.login_manager.post_login()
#             frappe.log_error(f"User {user_id} logged in successfully.")
#         except Exception as e:
#             frappe.log_error(f"Login Error: {str(e)}")
#             return {"success": False, "error": f"Login failed: {str(e)}"}

#         # login_manager = LoginManager()
#         # login_manager.authenticate(user=user_id, pwd=ىخىث)  # No password needed
#         # login_manager.post_login()

#         # Return session ID instead of setting a cookie
#         return {
#             "success": True,
#             "message": "Login successful",
#             "user_id": user_id,
#             "mobile_no": mobile_no,
#             "first_name":first_name,
#             "gender":gender,
#             "birth_date":birth_date,
#             "sid": frappe.session.sid  # Send session ID to Flutter
#         }


#     except Exception as e:
#         frappe.log_error(f"Login Error: {str(e)}")
#         return {"success": False, "error": str(e)}
#2
# @frappe.whitelist(allow_guest=True, methods=["GET"])
# def verify_otp(phone_number, otp):
#     try:
#         # الحد من المحاولات الفاشلة
#         attempts_key = f"otp_attempts_{phone_number}"
#         attempts = frappe.cache().get_value(attempts_key) or 0
#         if attempts >= 5:
#             return {"success": False, "error": "Too many failed attempts, try again later"}

#         # جلب وحذف OTP المخزن بعد استخدامه
#         stored_otp = frappe.cache().get_value(f"otp_{phone_number}")
#         frappe.cache().delete_value(f"otp_{phone_number}")

#         # التحقق من صحة OTP باستخدام `hmac.compare_digest`
#         if not stored_otp or not hmac.compare_digest(stored_otp, otp):
#             frappe.cache().set_value(attempts_key, attempts + 1, expires_in=600)  # منع الهجمات
#             return {"success": False, "error": "Invalid OTP"}

#         # استرجاع المستخدم والتأكد من دوره
#         user = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
#         if not user:
#             return {"success": False, "error": "User not found. Please complete registration."}

#         roles = frappe.get_roles(user)
#         if 'Simsaar App' in roles:
#             # إنشاء `access_token` و `refresh_token`
#             access_payload = {
#                 "user": user,
#                 "iat": datetime.utcnow(),  # إضافة وقت الإنشاء
#                 "exp": datetime.utcnow() + timedelta(hours=1)  # توكن صالح لساعة واحدة
#             }
#             refresh_payload = {
#                 "user": user,
#                 "iat": datetime.utcnow(),
#                 "exp": datetime.utcnow() + timedelta(days=30)  # توكن صالح لـ 30 يومًا
#             }

#             access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
#             refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

#             # إعادة المحاولات إلى الصفر عند النجاح
#             frappe.cache().delete_value(attempts_key)

#             return {
#                 "success": True,
#                 "message": "Login successful",
#                 "access_token": access_token,
#                 "refresh_token": refresh_token
#             }

#         return {
#             "success": False,
#             "message": "This is not a valid user",
#         }

#     except Exception as e:
#         error_message = f"Login Error: {str(e)[:100]}"
#         frappe.log_error(error_message)
#         return {"success": False, "error": "An error occurred, please try again"}


# @frappe.whitelist(allow_guest=True, methods=["POST"])
# def verify_otp(phone_number, otp):
#     try:
#         stored_otp = frappe.cache().get_value(f"otp_{phone_number}")
#         if not stored_otp or stored_otp != otp:
#             return {"success": False, "error": "Invalid OTP"}

#         # Check if user exists by phone number
#         user_id = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
#         if not user_id:
#             return {"success": False,"have_account":False, "error": "User not found. Please complete registration."}

#         # Fetch user details
       

#         # ✅ Generate API Key & Secret using Frappe's built-in function
#         roles = frappe.get_roles(user_id)
#         if 'Simsaar App' in roles:
#             user_details: User = frappe.get_doc("User", user_id)
#             api_secret = frappe.generate_hash(length=33)
#             # if api key is not set generate api key
#             if not user_details.api_key:
#                 api_key = frappe.generate_hash(length=17)
#                 user_details.api_key = api_key
#             else:
#                 api_key = user_details.api_key
#             user_details.api_secret = api_secret
#             user_details.save()

#             credentials = f"{api_key}:{api_secret}"  # Format as "username:password"
#             base64_encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
#             base64_encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
#             return {
#                 "success": True,
#                 "message": "Login successful",
#                 "have_account":True,
#                 "api_key": api_key,  # ✅ Use this for authentication
#                 "api_secret": api_secret,  # ✅ Secure authentication (only returned once)
#                 "base64_encoded":base64_encoded
#             }
#         else:
#             return {
#                 "success": False,
#                 "have_account":True,
#                 "message": "This is not a valid user",
#             }
#     except Exception as e:
#         frappe.log_error(f"Login Error: {str(e)}")
#         return {"success": False, "error": str(e)}


# @frappe.whitelist(allow_guest=True, methods=["GET"])
# def verify_otp(phone_number, otp):
#     """
#     التحقق من رمز OTP، الحد من المحاولات الفاشلة، وتسجيل الدخول باستخدام JWT.
#     """
#     try:
#         # منع المحاولات الفاشلة المتكررة
#         attempts_key = f"otp_attempts_{phone_number}"
#         attempts = frappe.cache().get_value(attempts_key) or 0
#         if attempts >= 5:
#             return {"success": False, "error": "عدد المحاولات الفاشلة تجاوز الحد المسموح، حاول لاحقًا"}

#         # جلب وحذف OTP المخزن بعد استخدامه
#         stored_otp = frappe.cache().get_value(f"otp_{phone_number}")
#         frappe.cache().delete_value(f"otp_{phone_number}")

#         # التحقق من صحة OTP باستخدام `hmac.compare_digest` لتجنب هجمات الـ timing attacks
#         if not stored_otp or not hmac.compare_digest(stored_otp, otp):
#             frappe.cache().set_value(attempts_key, attempts + 1, expires_in=600)  # منع الهجمات
#             return {"success": False, "error": "رمز التحقق غير صحيح"}

#         # استرجاع المستخدم
#         user = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
#         if not user:
#             return {"success": False, "error": "لم يتم العثور على المستخدم، الرجاء إكمال التسجيل"}

#         # التأكد من أن المستخدم يملك صلاحية Simsaar App
#         roles = frappe.get_roles(user)
#         if 'Simsaar App' in roles:
#             # إنشاء `access_token` و `refresh_token`
#             access_payload = {
#                 "user": user,
#                 "iat": datetime.utcnow(),
#                 "exp": datetime.utcnow() + timedelta(hours=1)  # صلاحية 1 ساعة
#             }
#             refresh_payload = {
#                 "user": user,
#                 "iat": datetime.utcnow(),
#                 "exp": datetime.utcnow() + timedelta(days=30)  # صلاحية 30 يومًا
#             }

#             access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
#             refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

#             # إعادة المحاولات إلى الصفر عند النجاح
#             frappe.cache().delete_value(attempts_key)

#             return {
#                 "success": True,
#                 "message": "تم تسجيل الدخول بنجاح",
#                 "access_token": access_token,
#                 "refresh_token": refresh_token
#             }

#         return {
#             "success": False,
#             "message": "هذا المستخدم غير مسموح له بالدخول",
#         }

#     except Exception as e:
#         error_message = f"Login Error: {str(e)}"
#         frappe.log_error(error_message)
#         return {"success": False, "error": "حدث خطأ، يرجى المحاولة مرة أخرى"}


# @frappe.whitelist(allow_guest=False,methods=["GET"])  # Only allow authenticated users
# def get_user_bookings():
#     try:
#         # ✅ Support API authentication
#         api_key = frappe.get_request_header("Authorization")
#         if api_key and "token" in api_key:
#             key_secret = api_key.replace("token ", "").split(":")
#             if len(key_secret) == 2:
#                 api_key, api_secret = key_secret
#                 user = frappe.db.get_value("User", {"api_key": api_key, "api_secret": api_secret}, "name")
#                 if not user:
#                     return {"error": "Invalid API credentials."}
#             else:
#                 return {"error": "Invalid API token format."}
#         else:
#             # ✅ Support session-based authentication
#             if not frappe.session.user or frappe.session.user == "Guest":
#                 return {"error": "Session invalid. Please log in first."}
#             user = frappe.session.user

#         # ✅ Fetch bookings for the logged-in user
#         user_bookings = frappe.get_all(
#             "Booking",
#             filters={"user": user},
#             fields=["name", "number_of_rooms", "guest_name", "mobile_number", 
#                     "room_type", "type", "check_in_date", "check_out_date", 
#                     "gust_number", "child_number"]
#         )

#         return {"success": True, "bookings": user_bookings}

#     except Exception as e:
#         frappe.log_error(f"Error fetching bookings: {str(e)}")
#         return {"success": False, "error": str(e)}
# @frappe.whitelist(allow_guest=False,methods=["PUT"])  # Only allow authenticated users
# def cancel_booking(booking_id):
#     try:
#         # ✅ Support API authentication
#         api_key = frappe.get_request_header("Authorization")
#         if api_key and "token" in api_key:
#             key_secret = api_key.replace("token ", "").split(":")
#             if len(key_secret) == 2:
#                 api_key, api_secret = key_secret
#                 user = frappe.db.get_value("User", {"api_key": api_key, "api_secret": api_secret}, "name")
#                 if not user:
#                     return {"error": "Invalid API credentials."}
#             else:
#                 return {"error": "Invalid API token format."}
#         else:
#             # ✅ Support session-based authentication
#             if not frappe.session.user or frappe.session.user == "Guest":
#                 return {"error": "Session invalid. Please log in first."}
#             user = frappe.session.user

#         # ✅ Fetch the booking to check ownership
#         if not frappe.db.exists("Booking", booking_id):
#             return {"error": "Booking not found."}

#         booking = frappe.get_doc("Booking", booking_id)

#         # ✅ Ensure the booking belongs to the logged-in user
#         if booking.user != user:
#             return {"error": "You are not authorized to cancel this booking."}

#         # ✅ Update the status to "Cancelled"
#         booking.status = "Cancelled"
#         booking.save(ignore_permissions=True)
#         frappe.db.commit()  # Ensure changes are saved

#         return {"success": True, "message": "Booking cancelled successfully."}

#     except Exception as e:
#         frappe.log_error(f"Error canceling booking: {str(e)}")
#         return {"success": False, "error": str(e)}
# @frappe.whitelist(allow_guest=False,methods=["GET"])  # Only allow authenticated users
# def get_user_details():
#     """Validate Basic Auth and return user details"""

#     auth_header = frappe.get_request_header("Authorization")

#     if not auth_header or not auth_header.startswith("Basic "):
#         frappe.throw("Missing or invalid Authorization header", frappe.AuthenticationError)

#     # Decode Base64 Authorization Header
#     try:
#         encoded_credentials = auth_header.split(" ")[1]
#         decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
#         api_key, api_secret = decoded_credentials.split(":")
#     except Exception:
#         frappe.throw("Invalid Authorization format", frappe.AuthenticationError)

#     # Validate API Key & Secret
#     user = frappe.db.get_value("User", {"api_key": api_key}, ["name", "full_name", "email", "api_secret"], as_dict=True)

#     if not user or user["api_secret"] != api_secret:
#         frappe.throw("Invalid API credentials", frappe.AuthenticationError)

#     # ✅ Return user details if authentication is successful
#     return {
#         "success": True,
#         "message": "Authentication successful",
#         "user_id": user["name"],
#         "full_name": user["full_name"],
#         "email": user["email"]
#     }


# def get_user_details():
#     try:
#         # ✅ Support API authentication
#         api_key = frappe.get_request_header("Authorization")
#         if api_key and "token" in api_key:
#             key_secret = api_key.replace("token ", "").split(":")
#             if len(key_secret) == 2:
#                 api_key, api_secret = key_secret
#                 user = frappe.db.get_value("User", {"api_key": api_key, "api_secret": api_secret}, "name")
#                 if not user:
#                     return {"error": "Invalid API credentials."}
#             else:
#                 return {"error": "Invalid API token format."}
#         else:
#             # ✅ Support session-based authentication
#             if not frappe.session.user or frappe.session.user == "Guest":
#                 return {"error": "Session invalid. Please log in first."}
#             user = frappe.session.user

#         # ✅ Check if user exists
#         if not frappe.db.exists("User", user):
#             return {"error": "User not found."}

#         # ✅ Fetch user details
#         user_doc = frappe.get_doc("User", user)
#         user_details = {
#             "full_name": user_doc.full_name,
#             "gender": user_doc.gender,
#             "birth_date": user_doc.birth_date,
#             "mobile_no": user_doc.mobile_no
#         }

#         return {"success": True, "user": user_details}

#     except Exception as e:
#         frappe.log_error(f"Error fetching user details: {str(e)}")
#         return {"success": False, "error": str(e)}


# def authenticate_request():
#     auth_header = frappe.get_request_header("Authorization")
#     if not auth_header or not auth_header.startswith("Bearer "):
#         frappe.throw("Invalid token format. Use 'Bearer <token>'")

#     token = auth_header.replace("Bearer ", "")

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         return payload["user"]
#     except jwt.ExpiredSignatureError:
#         frappe.throw("Token has expired. Please log in again.")
#     except jwt.InvalidTokenError:
#         frappe.throw("Invalid token. Please log in again.")







# @frappe.whitelist(allow_guest=True, methods=["POST"])
# def verify_otp(phone_number, otp):
#     try:
#         # ✅ Validate OTP
#         stored_otp = frappe.cache().get_value(f"otp_{phone_number}")
#         if not stored_otp or stored_otp != otp:
#             return {"success": False, "error": "Invalid OTP"}

#         # ✅ Check if user exists
#         user_id = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
#         if not user_id:
#             return {"success": False, "error": "User not found. Please complete registration."}

#         # ✅ Fetch user details securely
#         user_doc = frappe.get_doc("User", user_id)
#         user_data = {
#             "user_id": user_id,
#             "first_name": user_doc.first_name,
#             "last_name": user_doc.last_name,
#             "email": user_doc.email,
#             "mobile_no": user_doc.mobile_no,
#             "gender": user_doc.gender,
#             "birth_date": str(user_doc.birth_date) if user_doc.birth_date else None
#         }

#         # ✅ Generate OAuth Token (using Client ID & Secret)
#         oauth_token = get_token({
#             "grant_type": "password",
#             "client_id": "5oqvl9eo77",
#             "client_secret": "5dbc9cfa3c",
#             "username": user_id,
#             "password": "",  # Ensure OAuth authentication is configured
#         })

#         return {
#             "success": True,
#             "message": "Login successful",
#             "user": user_data,
#             "access_token": oauth_token["access_token"],  # ✅ Secure authentication
#             "expires_in": oauth_token["expires_in"],  # ✅ Token expiration time
#         }

#     except Exception as e:
#         frappe.log_error(f"Login Error: {str(e)}")
#         return {"success": False, "error": "Authentication failed"}






# @frappe.whitelist(allow_guest=False, methods=["GET"])  # Requires authentication
# def get_user_details():
#     """Validate Basic Auth and return user details"""

#     # auth_header = frappe.get_request_header("Authorization")

#     # if not auth_header or not auth_header.startswith("Basic "):
#     #     frappe.throw(_("Missing or invalid Authorization header"), frappe.AuthenticationError)

#     # try:
#     #     # Decode Base64 credentials
#     #     encoded_credentials = auth_header.split(" ")[1]
#     #     decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
#     #     api_key, api_secret = decoded_credentials.split(":")
#     # except Exception:
#     #     frappe.throw(_("Invalid Authorization format"), frappe.AuthenticationError)

#     # # Fetch user details by API Key
#     # user = frappe.db.get_value("User", {"api_key": api_key}, ["name", "full_name", "email", "api_secret"], as_dict=True)

#     # # Check if user exists and API secret is valid
#     # # if not user or frappe.generate_hash(user["api_secret"]) != frappe.generate_hash(api_secret):
#     # #     frappe.throw(_("Invalid API credentials"), frappe.AuthenticationError)

#     # # ✅ Return authenticated user details
#     # return {
#     #     "success": True,
#     #     "message": "Authentication successful",
#     #     "user_id": user["name"],
#     #     "full_name": user["full_name"],
#     #     "email": user["email"]
#     # }
#     session_id = frappe.session.sid  # Get session ID
#     session_data = Session(session_id).data
#     return {"session_data":session_data}




# @frappe.whitelist(allow_guest=False,methods=["POST"])  # Only allow authenticated users
# def booking(number_of_rooms, room_type, type, check_in_date, check_out_date, gust_number, child_number, places_prices):
#     try:
#         auth_header = frappe.get_request_header("Authorization")

#         if not auth_header or not auth_header.startswith("Basic "):
#             frappe.throw(_("Missing or invalid Authorization header"), frappe.AuthenticationError)

#         try:
#             # Decode Base64 credentials
#             encoded_credentials = auth_header.split(" ")[1]
#             decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
#             api_key, api_secret = decoded_credentials.split(":")
#         except Exception:
#             frappe.throw(_("Invalid Authorization format"), frappe.AuthenticationError)

#         user = frappe.db.get_value("User", {"api_key": api_key},"name", as_dict=True)

#         # ✅ Fetch user details
#         user_doc = frappe.get_doc("User", user)
#         user_full_name = user_doc.full_name
#         user_mobile_number = user_doc.mobile_no

#         # ✅ Prevent duplicate bookings
#         # existing_booking = frappe.db.exists("Booking", {"user": user, "check_in_date": check_in_date, "check_out_date": check_out_date})
#         # if existing_booking:
#         #     return {"error": "You already have a booking for these dates."}

#         # ✅ Create the booking document
#         booking_doc = frappe.get_doc({
#             "doctype": "Booking",
#             "number_of_rooms": number_of_rooms,
#             "guest_name": user_full_name,
#             "user": user.name,  
#             "mobile_number": user_mobile_number,
#             "room_type": room_type,
#             "type": type,
#             "check_in_date": check_in_date,
#             "check_out_date": check_out_date,
#             "gust_number": gust_number,
#             "child_number": child_number,
#             "places_prices": places_prices
#         })
#         booking_doc.insert(ignore_permissions=True)

#         # ✅ Prepare WhatsApp notification
#         booking_message = f"""
#         🏨 *حجز جديد*
#         🔹 *اسم العميل:* {user_full_name}
#         📱 *رقم الهاتف:* {user_mobile_number}
#         📅 *تسجيل الدخول:* {check_in_date}
#         📅 *تسجيل الخروج:* {check_out_date}
#         🛏️ *عدد الغرف:* {number_of_rooms}
#         👤 *عدد الضيوف:* {gust_number} | 👶 *أطفال:* {child_number}
#         💰 *السعر الإجمالي:* {places_prices}  
#         """

#         # ✅ List of admin phone numbers to notify
#         admin_phone_numbers = ["967778919884"]
#                 # admin_phone_numbers = ["967773552355", "967778919884"]

#         for phone_number in admin_phone_numbers:
#             try:
#                 frappe.call(
#                     "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
#                     recipient=phone_number,
#                     message=booking_message
#                 )
#             except Exception as e:
#                 frappe.log_error(f"WhatsApp message failed: {str(e)}")

#         return {
#             "success": True,
#             "message": "Booking created successfully",
#             "booking_id": booking_doc.name,  
#             "guest_name": user_full_name
#         }

#     except Exception as e:
#         frappe.log_error(f"Booking Error: {str(e)}")
#         return {"success": False, "error": str(e)}
@frappe.whitelist(allow_guest=True, methods=["POST"])
def register_user(phone_number, full_name, gender=None, birth_date=None):
    """
    Create a new user, assign role "simsaar app", and generate API credentials.
    """
    try:
        # Check if user already exists
        existing_user = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
        if existing_user:
            return {"success": False, "error": "User already exists."}

        # Generate a fake email to prevent duplicate issues
        today_with_time = now_datetime().strftime("%Y%m%d_%H%M%S")

        fake_email = f"user_{phone_number}_{today_with_time}@simsaarerp.net"

        # Create new user
        new_user = frappe.get_doc({
            "doctype": "User",
            "first_name": full_name,
            "mobile_no": phone_number,
            "email": fake_email,
            "birth_date": birth_date,
            "gender": gender,
            "username": phone_number,
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0
        })
        new_user.insert(ignore_permissions=True)


        existing_customer = frappe.db.get_value("Customer", {"mobile_no": phone_number}, "name")
        if not existing_customer:
            new_customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": full_name,
                "mobile_no": phone_number,
                "birthdate": birth_date,
                "customer_type":"Individual",
                "gender": gender,
                "user": new_user.name
            })
            new_customer.insert(ignore_permissions=True)
        else:
            # العميل موجود: حدّث مدير الحساب فقط
            frappe.db.set_value("Customer", existing_customer, "user", new_user.name)
        # ✅ Assign "simsaar app" role to the new user

        user_role = frappe.get_doc({
            "doctype": "Has Role",
            "parent": new_user.name,
            "parenttype": "User",
            "role": "simsaar app"
        })
        user_role.insert(ignore_permissions=True)

        # ✅ Authenticate user using LoginManager
        login_manager = LoginManager()
        login_manager.user = new_user.name  # ✅ Set user manually
        login_manager.post_login()  # ✅ Generate session & cookies

        # ✅ Set session expiry to **6 months** in "HH:MM:SS" format
        session_expiry = timedelta(days=360)  # 12 months
        total_seconds = int(session_expiry.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        formatted_expiry = f"{hours:02}:{minutes:02}:{seconds:02}"  # ✅ Format as HH:MM:SS

        session = frappe.session
        session.data["session_expiry"] = formatted_expiry  # ✅ Store in correct format
        session.update()

        # ✅ Extend session expiry for "Remember Me" (optional)
        frappe.local.session_obj.update({"session_expiry": formatted_expiry})
        frappe.db.commit()



        return {
            "success": True,
            "message": "User registered successfully",
            "sid": frappe.session.sid,  # ✅ Persistent session ID
            "expires_in": "8400:00:00"  # 1 year in seconds
            
        }

    except Exception as e:
        frappe.log_error(f"Registration Error: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True, methods=["POST"])
def verify_otp(phone_number, otp):
    try:
        # ✅ Validate OTP
        stored_otp = frappe.cache().get_value(f"otp_{phone_number}")
        if not stored_otp or stored_otp != otp:
            return {"success": False, "error": "Invalid OTP"}

        # ✅ Check if user exists
        user_id = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
        if not user_id:
            return {"success": False, "error": "User not found. Please complete registration."}

        # ✅ Authenticate user using LoginManager
        login_manager = LoginManager()
        login_manager.user = user_id  # Set user manually
        login_manager.post_login()

        # ✅ Set session expiry to **6 months** in `"HH:MM:SS"` format
        session = frappe.session
        session_expiry = timedelta(days=360)  # 12 months = 180 days
        total_seconds = int(session_expiry.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        formatted_expiry = f"{hours:02}:00:00"  # ✅ Format as HH:MM:SS

        session.data["session_expiry"] = formatted_expiry  # ✅ Store in same format
        session.update()

        # ✅ Extend session expiry (1 Year for "Remember Me")
        frappe.local.session_obj.update({"session_expiry": formatted_expiry})  # 1-year session
        frappe.db.commit()  # Save changes to the database

        # ✅ Fetch user details
        user_doc = frappe.get_doc("User", user_id)
        user_data = {
            "user_id": user_id,
            "first_name": user_doc.first_name,
            "last_name": user_doc.last_name,
            "email": user_doc.email,
            "mobile_no": user_doc.mobile_no,
            "gender": user_doc.gender,
            "birth_date": str(user_doc.birth_date) if user_doc.birth_date else None
        }

        return {
            "success": True,
            "message": "Login successful",
            "user": user_data,
            "sid": frappe.session.sid,  # ✅ Persistent session ID
            "expires_in": "8400:00:00"  # 1 year in seconds
        }

    except Exception as e:
        frappe.log_error(f"Login Error: {str(e)}")
        return {"success": False, "error": "Authentication failed"}


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_user_details():
    try:
        # ✅ Get the session user (Automatically extracts user from SID)
        user_id = frappe.session.user

        if not user_id or user_id == "Guest":
            return {"success": False, "error": "Unauthorized access"}

        # ✅ Fetch user details
        user_doc = frappe.get_doc("User", user_id)

        return {
            "success": True,
            "user_id": user_doc.name,
            # "email": user_doc.email,
            "full_name": user_doc.full_name,
            "mobile_no": user_doc.mobile_no,
            "gender": user_doc.gender,
            "birth_date": user_doc.birth_date
        }

    except Exception as e:
        frappe.log_error(f"User Fetch Error: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=False,methods=["POST"])  # Only allow authenticated users
def booking(number_of_rooms, room_type, type, check_in_date, check_out_date, gust_number, child_number, places_prices):
    try:
        # ✅ Get the session user (Automatically extracts user from SID)
        user_id = frappe.session.user

        if not user_id or user_id == "Guest":
            return {"success": False, "error": "Unauthorized access"}

        # ✅ Fetch user details
        user_doc = frappe.get_doc("User", user_id)

        # ✅ Prevent duplicate bookings
        # existing_booking = frappe.db.exists("Booking", {"user": user, "check_in_date": check_in_date, "check_out_date": check_out_date})
        # if existing_booking:
        #     return {"error": "You already have a booking for these dates."}
    

        existing_customer = frappe.db.get_value("Customer", {"user": user_id}, "name")

        customer = frappe.get_doc("Customer", existing_customer)

        # ✅ Create the booking document
        booking_doc = frappe.get_doc({
            "doctype": "Booking",
            "number_of_rooms": number_of_rooms,
            "guest_name": user_doc.full_name,
            "user": user_doc.name,  
            "mobile_number": user_doc.mobile_no,
            "room_type": room_type,
            "type": type,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "gust_number": gust_number,
            "child_number": child_number,
            "places_prices": places_prices,
            "customer": customer.name,
            "customer_name": customer.customer_name,
            "customer_mobile_no": customer.mobile_no,
        })
        booking_doc.insert(ignore_permissions=True)

        # ✅ Prepare WhatsApp notification
        booking_message = f"""
        🏨 *حجز جديد*
        🔹 *اسم العميل:* {user_doc.full_name}
        📱 *رقم الهاتف:* { user_doc.mobile_no}
        📅 *تسجيل الدخول:* {check_in_date}
        📅 *تسجيل الخروج:* {check_out_date}
        🛏️ *عدد الغرف:* {number_of_rooms}
        👤 *عدد الضيوف:* {gust_number} | 👶 *أطفال:* {child_number}
        💰 *السعر الإجمالي:* {places_prices}  
        """

        # ✅ List of admin phone numbers to notify
        admin_phone_numbers = ["967778919884"]
                # admin_phone_numbers = ["967773552355", "967778919884"]

        for phone_number in admin_phone_numbers:
            try:
                frappe.call(
                    "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
                    recipient=phone_number,
                    message=booking_message
                )
            except Exception as e:
                frappe.log_error(f"WhatsApp message failed: {str(e)}")

        return {
            "success": True,
            "message": "Booking created successfully",
            "booking_id": booking_doc.name,  
            "guest_name": user_doc.full_name
        }

    except Exception as e:
        frappe.log_error(f"Booking Error: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False,methods=["PUT"])  # Only allow authenticated users
def cancel_booking(booking_id):
    try:
        user_id = frappe.session.user

        if not user_id or user_id == "Guest":
            return {"success": False, "error": "Unauthorized access"}

        # ✅ Fetch user details
        user_doc = frappe.get_doc("User", user_id)

        # ✅ Fetch the booking to check ownership
        if not frappe.db.exists("Booking", booking_id):
            return {"error": "Booking not found."}

        booking = frappe.get_doc("Booking", booking_id)

        # ✅ Ensure the booking belongs to the logged-in user
        if booking.user != user_doc.name:
            return {"error": "You are not authorized to cancel this booking."}

        # ✅ Update the status to "Cancelled"
        booking.status = "Cancelled"
        booking.save(ignore_permissions=True)
        frappe.db.commit()  # Ensure changes are saved

        return {"success": True, "message": "Booking cancelled successfully."}

    except Exception as e:
        frappe.log_error(f"Error canceling booking: {str(e)}")
        return {"success": False, "error": str(e)}




@frappe.whitelist(allow_guest=False, methods=["GET"])  # Ensure only authenticated users can access
def get_user_bookings():
    try:
        # ✅ Ensure user is authenticated
        user_id = frappe.session.user
        if not user_id or user_id == "Guest":
            return {"success": False, "error": "Unauthorized access"}

        # ✅ Fetch bookings for the logged-in user
        user_bookings = frappe.get_all(
            "Booking",
            filters={"user": user_id},
            fields=[
                "name", "number_of_rooms", "guest_name", "mobile_number", 
                "room_type", "type", "check_in_date", "check_out_date", 
                "gust_number", "child_number","status"
            ]
        )

        # ✅ Fetch **full Places details** using `room_type`
        for booking in user_bookings:
            if booking.get("room_type"):  # Ensure `room_type` exists in Booking
                place = frappe.get_doc("Places", booking["room_type"])  # ✅ Fetch by `name`
                booking["places"] = place  # ✅ Attach full Place details

        return {"success": True, "bookings": user_bookings}

    except Exception as e:
        frappe.log_error(f"Error fetching bookings: {str(e)}")
        return {"success": False, "error": str(e)}





@frappe.whitelist(allow_guest=False,methods=["PUT"])  # Only allow authenticated users
def edit_user(full_name=None,birth_date=None,gender=None):
    try:
        user_id = frappe.session.user

        if not user_id or user_id == "Guest":
            return {"success": False, "error": "Unauthorized access"}



        # ✅ Fetch the booking to check ownership
        if not frappe.db.exists("User", user_id):
            return {"error": "User not found."}

        user = frappe.get_doc("User", user_id)



        # ✅ Update the status to "Cancelled"
        if full_name:
            user.first_name = full_name
            user.full_name = full_name

        if birth_date:
            user.birth_date = birth_date
        if gender:
            user.gender=gender
        user.save(ignore_permissions=True)
        frappe.db.commit()  # Ensure changes are saved

        return {"success": True, "message": "User edite  successfully."}

    except Exception as e:
        frappe.log_error(f"Error canceling booking: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])  # السماح فقط للمستخدمين المصادق عليهم
def complaints(description):
    try:
        # ✅ الحصول على المستخدم الحالي من الجلسة
        user_id = frappe.session.user

        if not user_id or user_id == "Guest":
            return {"success": False, "error": "الوصول غير مصرح به"}

        # ✅ جلب بيانات المستخدم
        user_doc = frappe.get_doc("User", user_id)

        # ✅ إنشاء مستند الشكوى
        complaints_doc = frappe.get_doc({
            "doctype": "Complaints",
            "user_name": user_doc.full_name,
            "user": user_doc.name,  
            "user_mobile_number": user_doc.mobile_no,
            "description": description
        })
        complaints_doc.insert(ignore_permissions=True)

        # ✅ إعداد رسالة إشعار الواتساب
        complaints_message = f"""
        📢 *شكوى او اقتراح  جديدة*
        🔹 *اسم العميل:* {user_doc.full_name}
        📱 *رقم الهاتف:* {user_doc.mobile_no}
        📝 *التفاصيل:* {description}
        """

        # ✅ قائمة أرقام المسؤولين لتلقي الإشعارات
        admin_phone_numbers = ["967778919884"]

        for phone_number in admin_phone_numbers:
            try:
                frappe.call(
                    "whatsapp_web.whatsapp_web.doctype.whatsapp_message.whatsapp_message.send_whatsapp_message",
                    recipient=phone_number,
                    message=complaints_message
                )
            except Exception as e:
                frappe.log_error(f"فشل إرسال رسالة واتساب: {str(e)}")

        return {
            "success": True,
            "message": "تم إرسال الشكوى بنجاح",
            "complaint_id": complaints_doc.name,  
            "user_name": user_doc.full_name
        }

    except Exception as e:
        frappe.log_error(f"خطأ في إرسال الشكوى: {str(e)}")
        return {"success": False, "error": f"حدث خطأ أثناء إرسال الشكوى: {str(e)}"}







@frappe.whitelist(allow_guest=True, methods=["GET"])  # Allow guest access
def get_hotspot(placeId):
    try:
        # ✅ Fetch hotspots related to the given placeId and order by creation time (oldest first)
        hotspots = frappe.get_all(
            "Hotspot",
            filters={"places": placeId},
            fields=["name"],
            order_by="creation asc"  # 👈 هذا هو السطر الذي يقوم بالترتيب
        )

        # ✅ Fetch child table data and format position as an array
        for hotspot in hotspots:
            child_records = frappe.get_all(
                "place rooms",  # Replace with actual child table name
                filters={"parent": hotspot["name"]},
                fields=["name", "position_x", "position_y", "position_z", "target"]
            )

            # ✅ Format position as an array
            for child in child_records:
                child["position"] = [
                    child.pop("position_x", 0),
                    child.pop("position_y", 0),
                    child.pop("position_z", 0)
                ]

            # ✅ Add child records to the parent hotspot
            hotspot["hotspots"] = child_records

        return {"success": True, "data": hotspots}

    except Exception as e:
        frappe.log_error(f"Error fetching hotspots: {str(e)}")
        return {"success": False, "error": str(e)}





@frappe.whitelist(allow_guest=True, methods=["POST"])
def saveHotspots():
    import json

    try:
        data = frappe.local.form_dict
        if isinstance(data, str):
            data = json.loads(data)

        places = data.get("places")
        hotspotName = data.get("hotspotName")
        facilitie = data.get("facilitie")
        hotspots = data.get("hotspots", [])

        if not places or not hotspots:
            return {"success": False, "error": "Missing required data"}

        inserted_names = []

        

        # ✅ Create Hotspot parent doc (if needed, or link to one)
        hotspot_doc = frappe.get_doc({
            "doctype": "Hotspot",
            "places": places,
            "facilitie": facilitie,
            "hotspot_name": hotspotName,
            "options": "place rooms",  # optional: set default
            "hotspots": []
        })
        for hotspot in hotspots:
            position = hotspot.get("position", [0, 0, 0])
            target = hotspot.get("target")
            # ✅ Add child row
            hotspot_doc.append("hotspots", {
                "doctype": "place rooms",  # replace with your actual child table Doctype
                "target": target,
                "position_x": position[0],
                "position_y": position[1],
                "position_z": position[2]
            })

        hotspot_doc.insert(ignore_permissions=True)
        inserted_names.append(hotspot_doc.name)

        return {
            "success": True,
            "message": "Hotspots saved successfully",
            "inserted": inserted_names
        }

    except Exception as e:
        frappe.log_error(f"Save Hotspots Error: {str(e)}")
        return {"success": False, "error": str(e)}




@frappe.whitelist(allow_guest=True, methods=["GET"])  # Ensure only authenticated users can access
def facilities():
    try:
        # ✅ Fetch bookings for the logged-in user
        facilities = frappe.get_all(
            "facilities",
            filters={"status": "نشط"},
            fields=[
                "name", "lowest_price", "property_type", "rating", 
                "facilitie_name", "formatted_address"
            ]
        )

            

        # 
        for facilitie in facilities:
            if facilitie.get("name"):  # 
                child_records = frappe.get_all(
                    "Facilities Gallery",
                    filters={"parent": facilitie["name"]},
                    fields=["image"],
                    order_by="CAST(name1 AS UNSIGNED) ASC"
                )
                facilitie["gallery"] = child_records

        return {"success": True, "Facilities": facilities}

    except Exception as e:
        frappe.log_error(f"Error fetching bookings: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["DELETE"])
def delete_user():
    try:
        user_id = frappe.session.user

        if not user_id or user_id == "Guest":
            return {"success": False, "error": "Unauthorized access"}



        # ✅ Fetch the booking to check ownership
        if not frappe.db.exists("User", user_id):
            return {"error": "User not found."}

        # Delete the user
        frappe.delete_doc("User", user_id, ignore_permissions=True)
        return {"success": True, "message": f"User {user_id} has been deleted"}

    except Exception as e:
        frappe.log_error(f"Delete User Error: {str(e)}")
        return {"success": False, "error": str(e)}




@frappe.whitelist(allow_guest=True, methods=["GET"])
def login_tester(phone_number, password):
    try:

        if  phone_number == 967784200010:
            return {"success": False, "error": "Unauthorized access"}

        user_id = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
        if not user_id:
            return {"success": False, "error": "User not found. Please complete registration."}

        # ✅ Authenticate user using LoginManager
        login_manager = LoginManager()
        login_manager.authenticate(user=phone_number, pwd=password)
        login_manager.post_login()

        # ✅ Set session expiry to **6 months** in `"HH:MM:SS"` format
        session = frappe.session
        session_expiry = timedelta(days=360)  # 12 months = 180 days
        total_seconds = int(session_expiry.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        formatted_expiry = f"{hours:02}:00:00"  # ✅ Format as HH:MM:SS

        session.data["session_expiry"] = formatted_expiry  # ✅ Store in same format
        session.update()

        # ✅ Extend session expiry (1 Year for "Remember Me")
        frappe.local.session_obj.update({"session_expiry": formatted_expiry})  # 1-year session
        frappe.db.commit()  # Save changes to the database

        # ✅ Fetch user details
        user_doc = frappe.get_doc("User", user_id)
        user_data = {
            "user_id": user_id,
            "first_name": user_doc.first_name,
            "last_name": user_doc.last_name,
            "email": user_doc.email,
            "mobile_no": user_doc.mobile_no,
            "gender": user_doc.gender,
            "birth_date": str(user_doc.birth_date) if user_doc.birth_date else None
        }

        return {
            "success": True,
            "message": "Login successful",
            "user": user_data,
            "sid": frappe.session.sid,  # ✅ Persistent session ID
            "expires_in": "8400:00:00"  # 1 year in seconds
        }

    except Exception as e:
        frappe.log_error(f"Delete User Error: {str(e)}")
        return {"success": False, "error": str(e)}