import frappe
from frappe.auth import LoginManager

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


@frappe.whitelist()
def booking(number_of_rooms, room_type, type, check_in_date, check_out_date, gust_number ,child_number):
    # Get the current user's full name
    user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name")
    
    # Create the booking document
    booking_doc = frappe.get_doc({
        "doctype": "Booking",
        "number_of_rooms": number_of_rooms,
        "guest_name": user_full_name,  # Set the guest name
        "user_name": frappe.session.user,
        "room_type":room_type,
        "type":type,
        "check_in_date":check_in_date,
        "check_out_date":check_out_date,
        "gust_number":gust_number,
        "child_number":child_number
    })
    booking_doc.insert(ignore_permissions=True)

    return {"message": "Booking created successfully", "guest_name": user_full_name}