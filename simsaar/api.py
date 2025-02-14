import frappe
from frappe.auth import LoginManager
from frappe import _
from datetime import datetime


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